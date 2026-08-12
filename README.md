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


## 프로그램 실행

이 프로젝트는 외부 Python 패키지를 사용하지 않습니다. Python 기본 설치만 있으면 실행할 수 있습니다.

```powershell
python main.py
```

## 설정 파일 위치

구분선, Feedback 접두문자, 최근 저장 위치는 사용자 PC의 다음 JSON 파일에 저장됩니다.

```text
%LOCALAPPDATA%\ISCPSR-Automation\settings.json
```

설정을 초기화하려면 프로그램을 종료한 뒤 이 파일을 삭제하면 됩니다.

## 배포 시 참고

- Python 설치와 패키지 설치가 모두 제한된 환경에서는 EXE 빌드 도구도 설치할 수 없습니다.
- 이 경우 Python이 이미 설치된 PC에서 `python main.py`로 실행하거나, 설치가 가능한 별도 환경에서 EXE를 빌드해야 합니다.
