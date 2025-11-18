@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ================================================
echo Plaka Tanıma Sistemi - Sunucu Başlatma
echo ================================================
echo.

:: Windows kontrolü
if not "%OS%"=="Windows_NT" (
    echo HATA: Bu program sadece Windows üzerinde çalışır.
    pause
    exit /b 1
)

:: Backend başlatma
echo [1/3] Backend başlatılıyor...
start "Plaka Tanıma Backend" cmd /k "cd /d %~dp0backend && call venv\Scripts\activate.bat && python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload"
echo [✓] Backend başlatıldı (Port: 8001)
echo.

:: Kısa bekleme
timeout /t 3 /nobreak >nul

:: Frontend başlatma
echo [2/3] Frontend başlatılıyor...
start "Plaka Tanıma Frontend" cmd /k "cd /d %~dp0frontend && yarn start"
echo [✓] Frontend başlatıldı (Port: 3000)
echo.

:: Tarayıcı açma
echo [3/3] Dashboard açılıyor...
timeout /t 5 /nobreak >nul
start http://localhost:3000
echo [✓] Dashboard tarayıcıda açıldı
echo.

echo ================================================
echo [✓] TÜM SERVİSLER ÇALIŞIYOR!
echo ================================================
echo.
echo Backend: http://localhost:8001
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8001/docs
echo.
echo Sunucuları durdurmak için açılan komut pencerelerini kapatın.
echo.
pause