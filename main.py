import json
import re
import shutil
import calendar
from datetime import date
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


# ============================================================
# 기본 설정
# ============================================================

APP_NAME = "ISCPSR 업무정리 자동화"

DEFAULT_SETTINGS = {
    "separator_char": "-",
    "separator_length": 99,
    "conversation_separator": True,
    "feedback_prefix": "#",
    "last_location": ""
}

# 사용자별 설정 저장 위치
SETTINGS_DIR = Path.home() / "AppData" / "Local" / "ISCPSR-Automation"
SETTINGS_FILE = SETTINGS_DIR / "settings.json"

# Windows 파일/폴더명에서 사용할 수 없는 문자
INVALID_FILENAME_CHARS = r'\/:*?"<>|'

# 업무용 첨부파일 허용 확장자
ALLOWED_EXTENSIONS = {
    ".txt",
    ".csv",
    ".tsv",
    ".md",
    ".log",
    ".rtf",

    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",

    ".pdf",

    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".bmp",
    ".webp",
    ".tif",
    ".tiff",

    ".hdf",
    ".h5",
    ".hdf5",

    ".json",
    ".xml",
    ".yaml",
    ".yml",

    ".zip",
    ".7z",
    ".rar",
    ".tar",
    ".gz",

    ".eml",
    ".msg"
}


class DatePicker(ttk.Frame):
    """외부 패키지 없이 사용하는 날짜 입력창과 팝업 달력."""

    WEEKDAYS = ("일", "월", "화", "수", "목", "금", "토")

    def __init__(self, master, on_date_selected=None):
        super().__init__(master)
        self.selected_date = date.today()
        self.display_year = self.selected_date.year
        self.display_month = self.selected_date.month
        self.on_date_selected = on_date_selected
        self.date_var = tk.StringVar()
        self.popup = None

        self.entry = ttk.Entry(self, textvariable=self.date_var, width=12, state="readonly")
        self.entry.pack(side="left")
        ttk.Button(self, text="▼", width=3, command=self.toggle_popup).pack(side="left", padx=(2, 0))
        self._update_entry()

    def get_date(self):
        return self.selected_date

    def set_date(self, value):
        self.selected_date = value
        self.display_year = value.year
        self.display_month = value.month
        self._update_entry()

    def _update_entry(self):
        self.date_var.set(self.selected_date.strftime("%Y-%m-%d"))

    def toggle_popup(self):
        if self.popup and self.popup.winfo_exists():
            self.close_popup()
        else:
            self.open_popup()

    def open_popup(self):
        self.display_year = self.selected_date.year
        self.display_month = self.selected_date.month
        self.popup = tk.Toplevel(self)
        self.popup.title("날짜 선택")
        self.popup.resizable(False, False)
        self.popup.transient(self.winfo_toplevel())
        self.popup.bind("<Escape>", lambda event: self.close_popup())
        self.render_calendar()
        self.popup.update_idletasks()
        self.popup.geometry(
            f"+{self.winfo_rootx()}+{self.winfo_rooty() + self.winfo_height()}"
        )
        # Windows에서 팝업이 메인 창 뒤로 숨지 않도록 화면 맨 앞으로 올린다.
        self.popup.deiconify()
        self.popup.lift()
        self.popup.attributes("-topmost", True)
        self.popup.after(100, lambda: self.popup and self.popup.winfo_exists() and self.popup.attributes("-topmost", False))
        self.popup.focus_set()

    def close_popup(self):
        if self.popup and self.popup.winfo_exists():
            self.popup.destroy()
        self.popup = None

    def change_year(self, offset):
        self.display_year += offset
        self.render_calendar()

    def change_month(self, offset):
        self.display_month += offset
        if self.display_month == 0:
            self.display_year -= 1
            self.display_month = 12
        elif self.display_month == 13:
            self.display_year += 1
            self.display_month = 1
        self.render_calendar()

    def select_date(self, day):
        self.selected_date = date(self.display_year, self.display_month, day)
        self._update_entry()
        self.close_popup()
        if self.on_date_selected:
            self.on_date_selected()

    def render_calendar(self):
        if not self.popup or not self.popup.winfo_exists():
            return
        for widget in self.popup.winfo_children():
            widget.destroy()

        header = ttk.Frame(self.popup, padding=5)
        header.pack(fill="x")
        # 요청한 순서대로 연도 선택은 왼쪽, 월 선택은 오른쪽에 표시한다.
        year_frame = ttk.Frame(header)
        year_frame.pack(side="left")
        ttk.Button(year_frame, text="‹", width=2, command=lambda: self.change_year(-1)).pack(side="left")
        ttk.Label(year_frame, text=f"{self.display_year}년", width=7, anchor="center").pack(side="left")
        ttk.Button(year_frame, text="›", width=2, command=lambda: self.change_year(1)).pack(side="left")

        month_frame = ttk.Frame(header)
        month_frame.pack(side="right")
        ttk.Button(month_frame, text="‹", width=2, command=lambda: self.change_month(-1)).pack(side="left")
        ttk.Label(month_frame, text=f"{self.display_month}월", width=4, anchor="center").pack(side="left")
        ttk.Button(month_frame, text="›", width=2, command=lambda: self.change_month(1)).pack(side="left")

        days = ttk.Frame(self.popup, padding=(5, 0, 5, 5))
        days.pack()
        for column, weekday in enumerate(self.WEEKDAYS):
            ttk.Label(days, text=weekday, width=3, anchor="center").grid(row=0, column=column, pady=(0, 2))

        for row, week in enumerate(calendar.Calendar(firstweekday=6).monthdayscalendar(self.display_year, self.display_month), start=1):
            for column, day in enumerate(week):
                if day:
                    ttk.Button(days, text=str(day), width=3, command=lambda value=day: self.select_date(value)).grid(row=row, column=column)
                else:
                    ttk.Label(days, text="", width=3).grid(row=row, column=column)


# ============================================================
# 설정 관리
# ============================================================

def load_settings():
    """
    사용자 설정을 불러온다.
    설정 파일이 없거나 깨져 있으면 기본값을 사용한다.
    """

    try:
        SETTINGS_DIR.mkdir(parents=True, exist_ok=True)

        if not SETTINGS_FILE.exists():
            save_settings(DEFAULT_SETTINGS.copy())
            return DEFAULT_SETTINGS.copy()

        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            settings = json.load(f)

        # 누락된 설정이 있으면 기본값으로 보완
        for key, value in DEFAULT_SETTINGS.items():
            if key not in settings:
                settings[key] = value

        return settings

    except Exception:
        return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    """
    사용자 설정 저장
    """

    SETTINGS_DIR.mkdir(parents=True, exist_ok=True)

    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)


# ============================================================
# 유틸리티
# ============================================================

def sanitize_text(value):
    """
    입력값 앞뒤 공백 제거
    """
    return value.strip()


def contains_invalid_filename_char(value):
    """
    Windows 파일명 금지문자 검사
    """

    for char in INVALID_FILENAME_CHARS:
        if char in value:
            return True, char

    # Windows에서 파일/폴더 이름 마지막에 공백 또는 . 사용 불가
    if value.endswith(" ") or value.endswith("."):
        return True, "파일명 마지막의 공백 또는 '.'"

    return False, None


def make_separator(settings):
    """
    설정값을 이용해 구분선을 생성
    """

    char = settings.get("separator_char", "-")
    length = settings.get("separator_length", 40)

    if not char:
        char = "-"

    try:
        length = int(length)
    except ValueError:
        length = 40

    length = max(1, min(length, 200))

    return char * length


def get_weekday_korean(date_obj):
    weekdays = [
        "월",
        "화",
        "수",
        "목",
        "금",
        "토",
        "일"
    ]

    return weekdays[date_obj.weekday()]


# ============================================================
# 메인 애플리케이션
# ============================================================

class Application(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title(APP_NAME)
        self.geometry("900x900")
        self.minsize(800, 700)

        self.settings = load_settings()

        # 대화내용 입력창 저장
        self.conversation_widgets = []

        # 첨부파일 목록
        self.attachments = []

        self.create_widgets()

    # --------------------------------------------------------
    # UI
    # --------------------------------------------------------

    def create_widgets(self):

        # ============================
        # 상단
        # ============================

        top_frame = ttk.Frame(self)
        top_frame.pack(fill="x", padx=15, pady=10)

        title_label = ttk.Label(
            top_frame,
            text=APP_NAME,
            font=("맑은 고딕", 18, "bold")
        )

        title_label.pack(side="left")

        settings_button = ttk.Button(
            top_frame,
            text="⚙ 설정",
            command=self.open_settings
        )

        settings_button.pack(side="right")

        # ============================
        # 스크롤 영역
        # ============================

        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(
            container,
            highlightthickness=0
        )

        scrollbar = ttk.Scrollbar(
            container,
            orient="vertical",
            command=self.canvas.yview
        )

        self.canvas.configure(
            yscrollcommand=scrollbar.set
        )

        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.main_frame = ttk.Frame(self.canvas)

        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.main_frame,
            anchor="nw"
        )

        self.main_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.bind(
            "<Configure>",
            self.resize_canvas
        )

        # Canvas 안의 Text/Entry 위에서도 휠로 전체 폼을 스크롤한다.
        self.bind_all("<MouseWheel>", self.on_mousewheel, add="+")
        self.bind_all("<Button-4>", self.on_mousewheel, add="+")
        self.bind_all("<Button-5>", self.on_mousewheel, add="+")

        # ============================
        # 저장 위치
        # ============================

        self.create_section_title(
            "저장 위치"
        )

        location_frame = ttk.Frame(self.main_frame)
        location_frame.pack(fill="x", padx=15, pady=5)

        self.location_var = tk.StringVar(
            value=self.settings.get("last_location", "")
        )

        ttk.Entry(
            location_frame,
            textvariable=self.location_var
        ).pack(
            side="left",
            fill="x",
            expand=True
        )

        ttk.Button(
            location_frame,
            text="찾아보기",
            command=self.select_location
        ).pack(
            side="left",
            padx=(5, 0)
        )

        # ============================
        # 기본 정보
        # ============================

        self.create_section_title(
            "기본 정보"
        )

        info_frame = ttk.Frame(self.main_frame)
        info_frame.pack(fill="x", padx=15)

        # 날짜
        ttk.Label(
            info_frame,
            text="날짜"
        ).grid(row=0, column=0, sticky="w", pady=5)

        date_frame = ttk.Frame(info_frame)
        date_frame.grid(row=0, column=1, sticky="w", pady=5)

        self.date_entry = DatePicker(
            date_frame,
            on_date_selected=self.update_weekday
        )

        self.date_entry.pack(side="left")

        # 요일 표시
        self.weekday_label = ttk.Label(
            date_frame,
            text=""
        )

        self.weekday_label.pack(
            side="left",
            padx=(5, 0),
        )

        self.update_weekday()

        # ISCPSR
        ttk.Label(
            info_frame,
            text="ISCPSR 번호"
        ).grid(row=1, column=0, sticky="w", pady=5)

        self.iscpsr_var = tk.StringVar()

        ttk.Entry(
            info_frame,
            textvariable=self.iscpsr_var
        ).grid(
            row=1,
            column=1,
            columnspan=2,
            sticky="ew",
            pady=5
        )

        # 오퍼링
        ttk.Label(
            info_frame,
            text="오퍼링"
        ).grid(row=2, column=0, sticky="w", pady=5)

        self.offering_var = tk.StringVar(
            value="PP"
        )

        offering_combo = ttk.Combobox(
            info_frame,
            textvariable=self.offering_var,
            values=["PP", "PS", "PG"],
            state="readonly",
            width=10
        )

        offering_combo.grid(
            row=2,
            column=1,
            sticky="w",
            pady=5
        )

        # POOL
        ttk.Label(
            info_frame,
            text="POOL"
        ).grid(row=3, column=0, sticky="w", pady=5)

        self.pool_var = tk.StringVar()

        ttk.Entry(
            info_frame,
            textvariable=self.pool_var
        ).grid(
            row=3,
            column=1,
            columnspan=2,
            sticky="ew",
            pady=5
        )

        # 프로젝트명
        ttk.Label(
            info_frame,
            text="프로젝트명"
        ).grid(row=4, column=0, sticky="w", pady=5)

        self.project_var = tk.StringVar()

        ttk.Entry(
            info_frame,
            textvariable=self.project_var
        ).grid(
            row=4,
            column=1,
            columnspan=2,
            sticky="ew",
            pady=5
        )

        # 생성자
        ttk.Label(
            info_frame,
            text="생성자/요청자"
        ).grid(row=5, column=0, sticky="w", pady=5)

        self.creator_var = tk.StringVar()

        ttk.Entry(
            info_frame,
            textvariable=self.creator_var
        ).grid(
            row=5,
            column=1,
            columnspan=2,
            sticky="ew",
            pady=5
        )

        info_frame.columnconfigure(1, weight=1)

        # ============================
        # Description
        # ============================

        self.create_section_title(
            "Description"
        )

        self.description_text = self.create_textbox(
            height=6
        )

        # ============================
        # 대화내용
        # ============================

        self.create_section_title(
            "대화내용"
        )

        self.conversation_frame = ttk.Frame(
            self.main_frame
        )

        self.add_conversation_button = ttk.Button(
            self.main_frame,
            text="+ 대화내용 추가",
            command=self.add_conversation
        )

        self.add_conversation_button.pack(
            anchor="w",
            padx=15,
            pady=5
        )

        # ============================
        # Feedback
        # ============================

        self.create_section_title(
            "최초 접수 Feedback"
        )

        self.first_feedback = self.create_textbox(
            height=6
        )

        self.create_section_title(
            "최종 답변 Feedback"
        )

        self.final_feedback = self.create_textbox(
            height=6
        )

        # ============================
        # 첨부파일
        # ============================

        self.create_section_title(
            "첨부파일"
        )

        self.attachment_frame = ttk.Frame(
            self.main_frame
        )

        self.attachment_frame.pack(
            fill="x",
            padx=15
        )

        ttk.Button(
            self.main_frame,
            text="+ 파일 추가",
            command=self.add_files
        ).pack(
            anchor="w",
            padx=15,
            pady=5
        )

        # ============================
        # 생성 버튼
        # ============================

        ttk.Separator(
            self.main_frame
        ).pack(
            fill="x",
            padx=15,
            pady=20
        )

        ttk.Button(
            self.main_frame,
            text="업무 폴더 생성",
            command=self.generate
        ).pack(
            pady=20,
            ipadx=30,
            ipady=8
        )

    # --------------------------------------------------------
    # UI Helper
    # --------------------------------------------------------

    def create_section_title(self, title):

        ttk.Label(
            self.main_frame,
            text=title,
            font=("맑은 고딕", 11, "bold")
        ).pack(
            anchor="w",
            padx=15,
            pady=(15, 5)
        )

    def create_textbox(self, height=5):

        frame = ttk.Frame(self.main_frame)
        frame.pack(fill="x", padx=15, pady=5)

        text = tk.Text(
            frame,
            height=height,
            wrap="word",
            font=("맑은 고딕", 10)
        )

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        text.pack(side="left", fill="both", expand=True)

        return text

    def resize_canvas(self, event):

        self.canvas.itemconfig(
            self.canvas_window,
            width=event.width
        )

    def on_mousewheel(self, event):
        """마우스 포인터가 폼 위에 있을 때만 세로 스크롤한다."""
        widget = self.winfo_containing(self.winfo_pointerx(), self.winfo_pointery())
        while widget is not None:
            if isinstance(widget, tk.Text):
                # 긴 내용은 폼이 아니라 해당 입력창을 스크롤한다.
                return
            widget = widget.master

        x = self.canvas.winfo_pointerx()
        y = self.canvas.winfo_pointery()
        left = self.canvas.winfo_rootx()
        top = self.canvas.winfo_rooty()
        inside_canvas = (
            left <= x < left + self.canvas.winfo_width()
            and top <= y < top + self.canvas.winfo_height()
        )
        if not inside_canvas:
            return

        if getattr(event, "num", None) == 4:
            units = -1
        elif getattr(event, "num", None) == 5:
            units = 1
        else:
            units = -int(event.delta / 120) if event.delta else 0

        if units:
            self.canvas.yview_scroll(units, "units")

    # --------------------------------------------------------
    # 날짜
    # --------------------------------------------------------

    def update_weekday(self, event=None):

        date_obj = self.date_entry.get_date()

        weekday = get_weekday_korean(
            date_obj
        )

        self.weekday_label.config(
            text=f"({weekday})"
        )

    # --------------------------------------------------------
    # 저장 위치
    # --------------------------------------------------------

    def select_location(self):

        directory = filedialog.askdirectory(
            title="업무 정리 폴더 선택"
        )

        if directory:
            self.location_var.set(
                directory
            )
            self.save_last_location(directory)

    def save_last_location(self, directory):
        self.settings["last_location"] = directory
        try:
            save_settings(self.settings)
        except OSError:
            # 저장 실패는 폴더 생성 기능을 막지 않도록 조용히 무시한다.
            pass

    # --------------------------------------------------------
    # 대화내용 추가
    # --------------------------------------------------------

    def add_conversation(self):

        if not self.conversation_widgets:
            self.conversation_frame.pack(
                fill="x",
                padx=15,
                before=self.add_conversation_button
            )

        frame = ttk.Frame(
            self.conversation_frame
        )

        frame.pack(
            fill="x",
            pady=5
        )

        index = len(
            self.conversation_widgets
        ) + 1

        label = ttk.Label(
            frame,
            text=f"대화내용 {index}"
        )

        label.pack(
            anchor="w"
        )

        text = tk.Text(
            frame,
            height=5,
            wrap="word",
            font=("맑은 고딕", 10)
        )

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        text.pack(
            side="left",
            fill="x",
            expand=True
        )

        delete_button = ttk.Button(
            frame,
            text="삭제",
            command=lambda f=frame, t=text:
            self.remove_conversation(f, t)
        )

        delete_button.pack(
            side="right",
            padx=5
        )

        self.conversation_widgets.append(
            (frame, text)
        )

        self.canvas.configure(
            scrollregion=self.canvas.bbox("all")
        )

    def remove_conversation(
        self,
        frame,
        text
    ):

        for item in self.conversation_widgets:

            if item[0] == frame:

                self.conversation_widgets.remove(
                    item
                )

                break

        frame.destroy()

        self.renumber_conversations()

        if not self.conversation_widgets:
            self.conversation_frame.pack_forget()

        self.after_idle(
            lambda: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

    def renumber_conversations(self):

        for index, item in enumerate(
            self.conversation_widgets,
            start=1
        ):

            frame = item[0]

            for widget in frame.winfo_children():

                if isinstance(
                    widget,
                    ttk.Label
                ):

                    widget.config(
                        text=f"대화내용 {index}"
                    )

    # --------------------------------------------------------
    # 첨부파일
    # --------------------------------------------------------

    def add_files(self):

        filetypes = [
            (
                "업무 첨부파일",
                " ".join(
                    f"*{ext}"
                    for ext in sorted(
                        ALLOWED_EXTENSIONS
                    )
                )
            ),
            (
                "모든 파일",
                "*.*"
            )
        ]

        files = filedialog.askopenfilenames(
            title="첨부파일 선택",
            filetypes=filetypes
        )

        if not files:
            return

        invalid_files = []

        for file in files:

            path = Path(file)

            if path.suffix.lower() not in ALLOWED_EXTENSIONS:

                invalid_files.append(
                    path.name
                )
                continue

            if str(path) not in self.attachments:

                self.attachments.append(
                    str(path)
                )

        if invalid_files:

            messagebox.showwarning(
                "첨부파일 확인",
                "허용되지 않은 확장자의 파일이 제외되었습니다.\n\n"
                + "\n".join(invalid_files)
            )

        self.refresh_attachment_list()

    def refresh_attachment_list(self):

        for widget in self.attachment_frame.winfo_children():
            widget.destroy()

        for index, file in enumerate(
            self.attachments
        ):

            frame = ttk.Frame(
                self.attachment_frame
            )

            frame.pack(
                fill="x",
                pady=2
            )

            ttk.Label(
                frame,
                text=f"📎 {Path(file).name}"
            ).pack(
                side="left"
            )

            ttk.Button(
                frame,
                text="삭제",
                command=lambda f=file:
                self.remove_attachment(f)
            ).pack(
                side="right"
            )

    def remove_attachment(self, file):

        if file in self.attachments:
            self.attachments.remove(file)

        self.refresh_attachment_list()

    # --------------------------------------------------------
    # 설정창
    # --------------------------------------------------------

    def open_settings(self):

        window = tk.Toplevel(self)

        window.title("양식 설정")
        window.geometry("430x330")
        window.resizable(False, False)

        frame = ttk.Frame(window)
        frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

        # 구분 문자
        ttk.Label(
            frame,
            text="구분선 문자"
        ).grid(
            row=0,
            column=0,
            sticky="w",
            pady=10
        )

        separator_var = tk.StringVar(
            value=self.settings["separator_char"]
        )

        ttk.Entry(
            frame,
            textvariable=separator_var,
            width=15
        ).grid(
            row=0,
            column=1,
            sticky="w"
        )

        # 구분선 길이
        ttk.Label(
            frame,
            text="구분선 길이"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            pady=10
        )

        length_var = tk.StringVar(
            value=str(
                self.settings["separator_length"]
            )
        )

        ttk.Entry(
            frame,
            textvariable=length_var,
            width=15
        ).grid(
            row=1,
            column=1,
            sticky="w"
        )

        # 대화내용 사이 구분선
        conversation_var = tk.BooleanVar(
            value=self.settings[
                "conversation_separator"
            ]
        )

        ttk.Checkbutton(
            frame,
            text="대화내용 사이 구분선 사용",
            variable=conversation_var
        ).grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="w",
            pady=10
        )

        # Feedback prefix
        ttk.Label(
            frame,
            text="Feedback 제목 접두문자"
        ).grid(
            row=3,
            column=0,
            sticky="w",
            pady=10
        )

        feedback_var = tk.StringVar(
            value=self.settings[
                "feedback_prefix"
            ]
        )

        ttk.Entry(
            frame,
            textvariable=feedback_var,
            width=15
        ).grid(
            row=3,
            column=1,
            sticky="w"
        )

        # 버튼
        button_frame = ttk.Frame(frame)

        button_frame.grid(
            row=5,
            column=0,
            columnspan=2,
            pady=25
        )

        def save():

            separator = separator_var.get()

            if not separator:
                messagebox.showerror(
                    "설정 오류",
                    "구분선 문자를 입력해주세요.",
                    parent=window
                )
                return

            try:
                length = int(
                    length_var.get()
                )

                if length < 1 or length > 200:
                    raise ValueError

            except ValueError:

                messagebox.showerror(
                    "설정 오류",
                    "구분선 길이는 1~200 사이의 숫자여야 합니다.",
                    parent=window
                )

                return

            new_settings = {
                "separator_char": separator,
                "separator_length": length,
                "conversation_separator":
                    conversation_var.get(),
                "feedback_prefix":
                    feedback_var.get(),
                "last_location": self.settings.get("last_location", "")
            }

            try:

                save_settings(
                    new_settings
                )

                self.settings = new_settings

                messagebox.showinfo(
                    "설정 저장",
                    "설정이 저장되었습니다.",
                    parent=window
                )

                window.destroy()

            except Exception as e:

                messagebox.showerror(
                    "설정 저장 실패",
                    str(e),
                    parent=window
                )

        ttk.Button(
            button_frame,
            text="취소",
            command=window.destroy
        ).pack(
            side="left",
            padx=5
        )

        ttk.Button(
            button_frame,
            text="저장",
            command=save
        ).pack(
            side="left",
            padx=5
        )

    # --------------------------------------------------------
    # 입력 검증
    # --------------------------------------------------------

    def validate_inputs(self):

        location = sanitize_text(
            self.location_var.get()
        )

        iscpsr = sanitize_text(
            self.iscpsr_var.get()
        )

        project = sanitize_text(
            self.project_var.get()
        )

        creator = sanitize_text(
            self.creator_var.get()
        )

        pool = sanitize_text(
            self.pool_var.get()
        )

        description = self.description_text.get(
            "1.0",
            "end"
        ).strip()

        first_feedback = self.first_feedback.get(
            "1.0",
            "end"
        ).strip()

        final_feedback = self.final_feedback.get(
            "1.0",
            "end"
        ).strip()

        missing = []

        if not location:
            missing.append(
                "저장 위치"
            )

        if not iscpsr:
            missing.append(
                "ISCPSR 번호"
            )

        if iscpsr and not iscpsr.isdigit():
            messagebox.showerror(
                "ISCPSR 번호 입력 오류",
                "ISCPSR 번호에는 숫자만 입력할 수 있습니다.\n\n예: 12345"
            )
            return None

        if not project:
            missing.append(
                "프로젝트명"
            )

        if not creator:
            missing.append(
                "생성자/요청자"
            )

        if not description:
            missing.append(
                "Description"
            )

        if not pool:
            missing.append(
                "POOL"
            )

        if not first_feedback:
            missing.append(
                "최초 접수 Feedback"
            )

        if not final_feedback:
            missing.append(
                "최종 답변 Feedback"
            )

        if missing:

            messagebox.showerror(
                "필수 입력값 확인",
                "다음 항목을 입력해주세요.\n\n"
                + "\n".join(
                    f"• {item}"
                    for item in missing
                )
            )

            return None

        # 저장 위치 확인
        location_path = Path(location)

        if not location_path.exists():

            messagebox.showerror(
                "저장 위치 오류",
                "지정한 저장 위치가 존재하지 않습니다."
            )

            return None

        # 폴더명 구성 요소 검사
        for label, value in [
            ("ISCPSR 번호", iscpsr),
            ("프로젝트명", project),
            ("생성자/요청자", creator)
        ]:

            invalid, char = contains_invalid_filename_char(
                value
            )

            if invalid:

                messagebox.showerror(
                    "폴더명 오류",
                    f"{label}에 Windows에서 사용할 수 없는 "
                    f"문자가 포함되어 있습니다.\n\n"
                    f"문제 문자: {char}\n\n"
                    f"사용할 수 없는 문자:\n"
                    f"{INVALID_FILENAME_CHARS}"
                )

                return None

        # 날짜
        date_obj = self.date_entry.get_date()

        weekday = get_weekday_korean(
            date_obj
        )

        date_string = (
            f"{date_obj.strftime('%Y-%m-%d')}"
            f"({weekday})"
        )

        offering = self.offering_var.get()

        folder_name = (
            f"{date_string}_"
            f"ISCPSR-{iscpsr}_"
            f"{offering}_"
            f"{project}"
            f"({creator})"
        )

        return {
            "location": location_path,
            "folder_name": folder_name,
            "project": project,
            "iscpsr": iscpsr,
            "offering": offering,
            "pool": sanitize_text(self.pool_var.get()),
            "creator": creator,
            "description": description
        }

    # --------------------------------------------------------
    # TXT 생성
    # --------------------------------------------------------

    def build_txt_content(self):

        separator = make_separator(
            self.settings
        )

        description = self.description_text.get(
            "1.0",
            "end"
        ).strip()

        content = []

        content.append(
            self.iscpsr_var.get().strip()
        )

        content.append("")

        content.append(
            description
        )

        content.append(
            separator
        )

        content.append(
            f"POOL: {self.pool_var.get().strip()}"
        )

        content.append(
            f"과제명,프로젝트명: "
            f"{self.project_var.get().strip()}"
        )

        content.append(
            f"생성자/요청자: "
            f"{self.creator_var.get().strip()}"
        )

        content.append(
            separator
        )

        # 대화내용
        conversations = []

        for frame, text_widget in self.conversation_widgets:

            value = text_widget.get(
                "1.0",
                "end"
            ).strip()

            if value:
                conversations.append(
                    value
                )

        for index, conversation in enumerate(
            conversations
        ):

            content.append(
                conversation
            )

            if (
                self.settings[
                    "conversation_separator"
                ]
                and index < len(conversations) - 1
            ):

                content.append(
                    separator
                )

        # 마지막 대화와 Feedback 사이에도 설정한 구분선을 넣는다.
        first_feedback = self.first_feedback.get(
            "1.0",
            "end"
        ).strip()

        final_feedback = self.final_feedback.get(
            "1.0",
            "end"
        ).strip()

        prefix = self.settings[
            "feedback_prefix"
        ]

        if conversations and (first_feedback or final_feedback):
            content.append(separator)

        if first_feedback:

            content.append("")

            content.append(
                f"{prefix}최초 접수 Feedback"
            )

            content.append("")

            content.append(
                first_feedback
            )

        if final_feedback:

            content.append("")

            content.append(
                f"{prefix}최종 답변 Feedback"
            )

            content.append("")

            content.append(
                final_feedback
            )

        return "\n".join(content) + "\n"

    # --------------------------------------------------------
    # 생성
    # --------------------------------------------------------

    def generate(self):
        # 한글 IME 조합 중 버튼을 눌렀을 때 마지막 글자가 누락되는 현상을 줄인다.
        self.after_idle(self._generate)

    def _generate(self):

        data = self.validate_inputs()

        if not data:
            return

        root = data["location"]
        self.save_last_location(str(root))

        folder_path = (
            root / data["folder_name"]
        )

        # 중복 검사
        if folder_path.exists():

            result = messagebox.askyesno(
                "폴더가 이미 존재합니다",
                f"다음 폴더가 이미 존재합니다.\n\n"
                f"{folder_path}\n\n"
                f"기존 폴더를 열겠습니까?"
            )

            if result:

                try:
                    import os
                    os.startfile(
                        str(folder_path)
                    )

                except Exception as e:

                    messagebox.showerror(
                        "오류",
                        str(e)
                    )

            return

        # TXT 이름
        txt_name = (
            f"{data['project']}.txt"
        )

        txt_path = (
            folder_path / txt_name
        )

        # 미리보기
        attachment_names = [
            Path(file).name
            for file in self.attachments
        ]

        preview = (
            f"생성될 폴더\n"
            f"{folder_path}\n\n"
            f"TXT 파일\n"
            f"{txt_name}\n\n"
            f"첨부파일 ({len(attachment_names)}개)\n"
        )

        if attachment_names:

            preview += "\n".join(
                f"• {name}"
                for name in attachment_names
            )

        else:

            preview += "없음"

        preview += "\n\n위 내용으로 생성하시겠습니까?"

        result = messagebox.askyesno(
            "생성 확인",
            preview
        )

        if not result:
            return

        try:

            # 폴더 생성
            folder_path.mkdir(
                parents=True,
                exist_ok=False
            )

            # TXT 생성
            content = self.build_txt_content()

            with open(
                txt_path,
                "w",
                encoding="utf-8-sig"
            ) as f:

                f.write(content)

            # 첨부파일 복사
            copied_files = []

            for file in self.attachments:

                source = Path(file)

                if not source.exists():
                    continue

                destination = (
                    folder_path /
                    source.name
                )

                # 동일 파일명이 있는 경우
                if destination.exists():

                    stem = destination.stem
                    suffix = destination.suffix

                    counter = 1

                    while destination.exists():

                        destination = (
                            folder_path /
                            f"{stem}({counter}){suffix}"
                        )

                        counter += 1

                shutil.copy2(
                    source,
                    destination
                )

                copied_files.append(
                    destination.name
                )

            messagebox.showinfo(
                "생성 완료",
                f"업무 폴더가 생성되었습니다.\n\n"
                f"{folder_path}"
            )

            # 생성된 폴더 열기
            result = messagebox.askyesno(
                "폴더 열기",
                "생성된 업무 폴더를 열겠습니까?"
            )

            if result:

                import os

                os.startfile(
                    str(folder_path)
                )

        except PermissionError:

            # 실패한 경우 생성된 폴더가 있다면 제거하지 않는다.
            messagebox.showerror(
                "권한 오류",
                "파일 또는 폴더에 접근할 권한이 없습니다.\n\n"
                "K드라이브 연결 상태와 쓰기 권한을 확인해주세요."
            )

        except OSError as e:

            messagebox.showerror(
                "파일 생성 오류",
                f"파일 또는 폴더 생성 중 오류가 발생했습니다.\n\n"
                f"{e}"
            )

        except Exception as e:

            messagebox.showerror(
                "알 수 없는 오류",
                f"작업 중 오류가 발생했습니다.\n\n"
                f"{e}"
            )


# ============================================================
# 실행
# ============================================================

if __name__ == "__main__":

    app = Application()

    app.mainloop()
