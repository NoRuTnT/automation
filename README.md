# ISCPSR 업무정리 자동화

업무 폴더와 정리용 TXT 파일을 자동으로 만들고, 선택한 첨부파일을 함께 복사하는 Windows용 Python 프로그램입니다.

## 사전 준비

- Windows 10 또는 11
- [Python 3.12 이상](https://www.python.org/downloads/) 설치

Python 설치 화면에서는 **Add Python to PATH**를 반드시 선택합니다.

## 사용 전 알아둘 점

### 필수 입력값

- 저장 위치
- ISCPSR 번호: **숫자만** 입력할 수 있습니다. 예: `12345`
- 프로젝트명
- 생성자/요청자
- Description
- POOL
- 최초 접수 Feedback
- 최종 답변 Feedback

대화내용과 첨부파일만 선택 입력입니다.

### 폴더명 제한

ISCPSR 번호, 프로젝트명, 생성자/요청자는 생성될 폴더명에 사용됩니다. 따라서 Windows 폴더명에 사용할 수 없는 아래 문자는 입력할 수 없습니다.

```text
\ / : * ? " < > |
```

또한 값의 마지막은 공백이나 마침표(`.`)로 끝날 수 없습니다.

### 첨부할 수 있는 파일

아래 확장자의 파일만 첨부할 수 있습니다.

- 문서·텍스트: `.txt`, `.csv`, `.tsv`, `.md`, `.log`, `.rtf`, `.doc`, `.docx`, `.xls`, `.xlsx`, `.ppt`, `.pptx`, `.pdf`
- 이미지: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.webp`, `.tif`, `.tiff`
- 데이터·설정: `.hdf`, `.h5`, `.hdf5`, `.json`, `.xml`, `.yaml`, `.yml`
- 압축 파일: `.zip`, `.7z`, `.rar`, `.tar`, `.gz`
- 메일: `.eml`, `.msg`


## 실행 환경 설치

PowerShell을 열고 프로젝트 폴더에서 아래 명령을 순서대로 실행합니다.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install tkcalendar pyinstaller
```

`python -m venv .venv`는 프로젝트 전용 Python 환경을 만들고, `Activate.ps1`은 그 환경을 현재 PowerShell에서 사용하도록 켭니다. 이렇게 하면 `tkcalendar`, `pyinstaller` 같은 패키지와 버전이 PC의 다른 Python 프로젝트에 영향을 주지 않습니다. EXE만 실행할 사용자에게는 이 과정이 필요 없습니다.

PowerShell의 실행 정책 오류가 나면, 현재 창에서만 아래 명령을 먼저 실행한 뒤 다시 활성화합니다.

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## 프로그램 실행

가상환경을 활성화한 상태에서 실행합니다.

```powershell
python main.py
```

## EXE 만들기

가상환경을 활성화한 상태에서 다음 명령을 실행합니다.

```powershell
pyinstaller --noconfirm --clean --onefile --noconsole --collect-all tkcalendar --name "업무정리 자동화" main.py
```

완료되면 실행 파일은 아래 경로에 생성됩니다.

```text
dist\업무정리 자동화.exe
```

`--noconsole` 옵션으로 실행 시 검은 콘솔 창이 표시되지 않습니다. 오류 원인을 확인해야 할 때는 이 옵션을 뺀 뒤 다시 빌드하세요.

```powershell
pyinstaller --noconfirm --clean --onefile --collect-all tkcalendar --name "업무정리 자동화" main.py
```

## 설정 파일 위치

구분선, Feedback 접두문자, 최근 저장 위치는 사용자 PC의 다음 JSON 파일에 저장됩니다.

```text
%LOCALAPPDATA%\ISCPSR-Automation\settings.json
```

설정을 초기화하려면 프로그램을 종료한 뒤 이 파일을 삭제하면 됩니다.

## 배포 시 참고

- 다른 PC에는 `dist\업무정리 자동화.exe` 파일만 전달하면 됩니다.
- Windows Defender 또는 회사 보안 프로그램이 새 EXE 파일을 검사할 수 있습니다. 신뢰할 수 있는 내부 배포 경로를 사용하세요.
- EXE를 수정하려면 Python 원본인 `main.py`를 변경한 후 위 EXE 빌드 명령을 다시 실행합니다.
