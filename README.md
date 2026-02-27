WINGS ↔ SAM 옵션 코드 비교 (Streamlit 앱)
=====================================

간단 소개
---------
- 이 저장소는 `streamlit_app.py` 기반의 WINGS와 SAM 옵션 코드 비교 웹앱을 포함합니다.
- 팀원들이 웹 링크로 접속하여 WINGS 엑셀/CSV와 SAM `.docx` 파일을 업로드하고, 옵션 코드 차이를 비교할 수 있도록 설계되었습니다.

빠른 시작 (로컬)
-----------------
1. Python 3.8+ 가 설치되어 있는지 확인합니다.
2. 가상환경 생성 및 활성화:

```powershell
python -m venv .venv
& .venv\Scripts\Activate.ps1
```

3. 의존성 설치:

```powershell
pip install -r requirements.txt
```

4. 앱 실행:

```powershell
streamlit run streamlit_app.py
```

배포 (Streamlit Community Cloud 권장)
-----------------------------------
1. GitHub에 새 리포지토리를 생성합니다.
2. 이 로컬 레포지토리를 리모트에 연결하고 푸시합니다:

```powershell
git remote add origin https://github.com/<your-org-or-user>/<repo>.git
git branch -M main
git push -u origin main
```

3. https://share.streamlit.io 에 접속하여 GitHub 계정으로 로그인 후, 위 리포지토리를 연결하고 브랜치(`main`)와 앱 파일(`streamlit_app.py`)을 지정하면 즉시 배포됩니다.

대체 배포(예: Heroku/Render)
--------------------------
- `Procfile`이 포함되어 있어 Heroku/다른 PaaS에도 배포할 수 있습니다. 필요 시 추가 가이드를 제공합니다.

보안(선택)
---------
- 팀 접근 제어를 위해 `streamlit-authenticator`를 사용해 로그인 기능을 추가할 수 있습니다. 현재 `requirements.txt`에 포함되어 있으나, 배포 시 비밀번호/해시를 비공개 시크릿으로 설정하세요.

파일/폴더 설명
---------------
- `streamlit_app.py`: 메인 애플리케이션
- `requirements.txt`: Python 의존성
- `Procfile`: PaaS 배포용 실행 명령
- `.streamlit/config.toml`: Streamlit 런타임 설정

다음 단계
--------
원하시면 제가 다음을 대신 진행해 드립니다:

- 로컬에서 `git init` 및 초기 커밋 수행(이미 실행할 수 있음).
- 리모트 GitHub 레포 생성 및 푸시(토큰/권한 필요).
- Streamlit Cloud에 연결해 실제 배포(로그인 필요).

문의사항이나 자동화 원하시면 알려주세요.
# WINGS vs SAM 비교 대시보드

간단한 Streamlit 기반 대시보드 예제입니다. WINGS에서 Export한 CSV/Excel 파일과 SAM(.docx/.csv) 파일을 업로드하면 `Commission no.` 기준으로 옵션 코드 차이를 계산해 줍니다.

설치 및 실행

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

사용법
- `WINGS CSV/Excel 파일`을 업로드합니다. (필수)
- `SAM` 파일(.docx/.csv)을 여러 개 업로드할 수 있습니다.
- 결과 표를 보고 Excel로 다운로드하세요.

비고
- SAM 파일에서 모델(`Baumuster`) 추출은 파일명/문서 내 `Model`/`Baumuster` 키워드 검색을 시도합니다. 파일 포맷이 다르면 간단한 전처리가 필요할 수 있습니다.
