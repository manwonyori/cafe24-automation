@echo off
echo ========================================
echo   카페24 자동화 시스템 로컬 실행
echo ========================================
echo.

cd /d %~dp0

echo [1] Python 환경 확인 중...
python --version
if errorlevel 1 (
    echo [오류] Python이 설치되어 있지 않습니다.
    pause
    exit /b 1
)

echo.
echo [2] 필요한 패키지 설치 중...
pip install -r requirements.txt

echo.
echo [3] 시스템 검증 중...
python src\verify_api.py

echo.
echo [4] 웹 서버 시작 중...
echo 브라우저에서 http://localhost:5000 접속
echo.
python src\web_app.py

pause