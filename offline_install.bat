@echo off
setlocal enabledelayedexpansion

echo ================================================
echo OFFLINE KURULUM - PLAKA TANIMA SISTEMI
echo ================================================
echo.
echo Bu script INTERNET BAGLANTISI OLMADAN kurulum yapar.
echo.
echo Gereksinimler:
echo - Python 3.12 ^(KURULU olmali^)
echo - Node.js 16+ ^(KURULU olmali^)
echo - MongoDB ^(KURULU ve CALISIR olmali^)
echo - offline_installer klasoru bu dizinde olmali
echo.
pause

REM Offline installer klasorunu kontrol et
if not exist "offline_installer" (
    echo [ERROR] offline_installer klasoru bulunamadi!
    echo.
    echo Lutfen once create_offline_installer.bat calistirarak
    echo offline installer olusturun ve bu klasoru buraya kopyalayin.
    pause
    exit /b 1
)

echo [1/7] Python kontrol ediliyor...
py --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python bulunamadi!
    echo Python 3.12 yuklu olmali.
    pause
    exit /b 1
)
py --version
echo.

echo [2/7] Node.js kontrol ediliyor...
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js bulunamadi!
    echo Node.js 16+ yuklu olmali.
    pause
    exit /b 1
)
node --version
echo.

REM Proje klasor yapisini olustur
echo [3/7] Proje klasor yapisi olusturuluyor...
if not exist "backend" mkdir backend
if not exist "frontend" mkdir frontend
echo Klasorler olusturuldu.
echo.

REM Backend dosyalarini kopyala
echo [4/7] Backend dosyalari kopyalaniyor...
copy /Y offline_installer\scripts\requirements.txt backend\
copy /Y offline_installer\scripts\backend.env backend\.env
echo Backend dosyalari kopyalandi.
echo.

REM Backend virtual environment olustur ve paketleri yukle
echo [5/7] Backend paketleri OFFLINE yukleniyor...
cd /d "%~dp0backend"

if exist "venv" (
    echo Mevcut venv temizleniyor...
    rmdir /s /q venv
)

echo Virtual environment olusturuluyor...
py -m venv venv
call venv\Scripts\activate.bat

echo pip guncelleniyor...
py -m pip install --upgrade pip --no-index --find-links="%~dp0offline_installer\backend_packages"

echo Backend paketleri OFFLINE yukleniyor...
echo Bu islem 5-10 dakika surebilir...
pip install --no-index --find-links="%~dp0offline_installer\backend_packages" -r requirements.txt

if errorlevel 1 (
    echo [ERROR] Backend paketleri OFFLINE yuklenemedi!
    pause
    exit /b 1
)

echo Backend paketleri basariyla yuklendi.
echo.

REM Frontend dosyalarini kopyala ve paketleri yukle
echo [6/7] Frontend paketleri OFFLINE yukleniyor...
cd /d "%~dp0"

REM package.json varsa kopyala
if exist "offline_installer\scripts\package.json" (
    copy /Y offline_installer\scripts\package.json frontend\
)

cd frontend

REM .env.local olustur
if not exist ".env.local" (
    echo Creating .env.local for local development...
    echo REACT_APP_BACKEND_URL=http://localhost:8001 > .env.local
    echo .env.local created
)

REM node_modules.zip varsa ac
if exist "%~dp0offline_installer\frontend_packages\node_modules.zip" (
    echo node_modules arsivi aciliyor...
    echo Bu islem 2-5 dakika surebilir...
    powershell -Command "Expand-Archive -Path '%~dp0offline_installer\frontend_packages\node_modules.zip' -DestinationPath '.' -Force"
    
    if errorlevel 1 (
        echo [ERROR] node_modules arsivi acilamadi!
        pause
        exit /b 1
    )
    
    echo Frontend paketleri basariyla yuklendi.
    
    REM Craco kontrolu
    if not exist "node_modules\.bin\craco.cmd" (
        echo [WARNING] craco bulunamadi offline paketlerde!
        echo Bu sorun olabilir. Lutfen internet baglantisi ile yeniden kurun.
    ) else (
        echo [OK] craco mevcut ve hazir
    )
) else (
    echo [ERROR] node_modules.zip bulunamadi!
    pause
    exit /b 1
)

echo.

REM MongoDB kontrolu
echo [7/7] MongoDB kontrol ediliyor...
echo MongoDB servisinin calistigindan emin olun.
echo Windows Hizmetler ^(services.msc^) - MongoDB servisi
echo.

cd /d "%~dp0"

echo ================================================
echo [BASARILI] Offline kurulum tamamlandi!
echo ================================================
echo.
echo SERVISLERI BASLATMAK ICIN:
echo.
echo Seceneк 1: start_server.bat calistirin
echo Seceneк 2: Manuel baslatma:
echo.
echo Backend:
echo   cd backend
echo   venv\Scripts\activate
echo   py -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload
echo.
echo Frontend:
echo   cd frontend
echo   set PORT=3000
echo   yarn start
echo.
echo ================================================
echo.

REM start_server.bat varsa kopyala
if exist "offline_installer\scripts\start_server.bat" (
    copy /Y offline_installer\scripts\start_server.bat .
    echo start_server.bat kopyalandi.
    echo.
    echo Servisleri baslatmak icin start_server.bat calistirin.
)

echo Kurulum tamamlandi!
echo.
pause

REM Kullaniciya servisleri baslatma secenegi sun
echo.
set /p START_NOW="Servisleri simdi baslatmak ister misiniz? (E/H): "
if /i "%START_NOW%"=="E" (
    if exist "start_server.bat" (
        call start_server.bat
    ) else (
        echo start_server.bat bulunamadi. Manuel baslatma gerekli.
    )
)
