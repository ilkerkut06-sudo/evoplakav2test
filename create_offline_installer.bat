@echo off
setlocal enabledelayedexpansion

echo ================================================
echo OFFLINE INSTALLER OLUSTURUCU
echo ================================================
echo.
echo Bu script tum paketleri indirecek ve offline kurulum
echo icin hazir hale getirecek.
echo.
echo Gereksinimler:
echo - Internet baglantisi
echo - Python 3.12
echo - Node.js
echo.
pause

REM Offline klasorunu olustur
echo [1/6] Offline klasor olusturuluyor...
if not exist "offline_installer" mkdir offline_installer
cd offline_installer

REM Alt klasorleri olustur
if not exist "backend_packages" mkdir backend_packages
if not exist "frontend_packages" mkdir frontend_packages
if not exist "scripts" mkdir scripts
echo Klasorler olusturuldu.
echo.

REM Python paketlerini indir
echo [2/6] Backend Python paketleri indiriliyor...
echo Bu islem 5-10 dakika surebilir (PyTorch, EasyOCR buyuk paketler)...
cd /d "%~dp0"
py -m pip download -r backend\requirements.txt -d offline_installer\backend_packages
if errorlevel 1 (
    echo [ERROR] Backend paketleri indirilemedi!
    pause
    exit /b 1
)
echo Backend paketleri indirildi: offline_installer\backend_packages\
echo.

REM Frontend paketlerini indir
echo [3/6] Frontend paketleri indiriliyor...
cd /d "%~dp0frontend"

REM Yarn varsa yarn kullan
where yarn >nul 2>&1
if errorlevel 1 (
    echo Yarn bulunamadi, npm ile devam ediliyor...
    npm install --legacy-peer-deps
) else (
    echo Yarn ile paketler yukleniyor...
    yarn install
)

if errorlevel 1 (
    echo [ERROR] Frontend paketleri indirilemedi!
    pause
    exit /b 1
)

echo Frontend paketleri yuklendi: frontend\node_modules\
echo.

REM Frontend node_modules'u ziplemek icin PowerShell kullan
echo [4/6] Frontend paketleri arsivleniyor...
cd /d "%~dp0"
powershell -Command "Compress-Archive -Path 'frontend\node_modules' -DestinationPath 'offline_installer\frontend_packages\node_modules.zip' -Force"
if errorlevel 1 (
    echo [WARNING] node_modules ziplenirken hata olustu.
    echo Devam ediliyor...
)
echo Frontend paketleri arsivlendi: offline_installer\frontend_packages\node_modules.zip
echo.

REM Gerekli script dosyalarini kopyala
echo [5/6] Script dosyalari kopyalaniyor...
copy /Y setup_and_start.bat offline_installer\scripts\
copy /Y start_server.bat offline_installer\scripts\
copy /Y backend\requirements.txt offline_installer\scripts\
copy /Y backend\.env offline_installer\scripts\backend.env
copy /Y frontend\package.json offline_installer\scripts\
echo Script dosyalari kopyalandi.
echo.

REM README olustur
echo [6/6] README dosyasi olusturuluyor...
(
echo OFFLINE INSTALLER - PLAKA TANIMA SISTEMI
echo ==========================================
echo.
echo Bu klasor internet baglantisi olmadan kurulum yapmak icin tum gereklilikleri icerir.
echo.
echo ICERIK:
echo - backend_packages/    : Python paketleri ^(wheel dosyalari^)
echo - frontend_packages/   : Node.js paketleri ^(node_modules.zip^)
echo - scripts/             : Kurulum script'leri
echo.
echo KURULUM ADIMLARI:
echo.
echo 1. Python 3.12 ve Node.js'in KURULU oldugunu dogrulayin
echo    ^(Internet gerektirmez, onceden kurulmali^)
echo.
echo 2. MongoDB'nin KURULU ve CALISIR oldugunu dogrulayin
echo.
echo 3. Bu klasoru hedef makineye kopyalayin
echo.
echo 4. offline_install.bat dosyasini calistirin
echo.
echo 5. Kurulum tamamlandiginda tarayiciniz otomatik acilacak
echo.
echo NOTLAR:
echo - Kurulum sirasinda internet baglantisi gerekmez
echo - Python, Node.js, MongoDB onceden kurulu olmali
echo - Toplam boyut: ~2-3 GB ^(PyTorch, EasyOCR buyuk paketler^)
echo.
echo Olusturma Tarihi: %date% %time%
) > offline_installer\README.txt

echo.
echo ================================================
echo [BASARILI] Offline installer hazir!
echo ================================================
echo.
echo Konum: offline_installer\
echo.
echo Icindekiler:
echo - backend_packages\ : Python paketleri
echo - frontend_packages\ : Node.js paketleri
echo - scripts\ : Kurulum dosyalari
echo - README.txt : Kullanim kilavuzu
echo.
echo SONRAKI ADIM:
echo 1. offline_install.bat dosyasini olusturmak icin bu pencereyi kapatin
echo 2. Agent size offline_install.bat dosyasini verecek
echo 3. offline_installer\ klasorunu hedef makineye kopyalayin
echo 4. Hedef makinede offline_install.bat calistirin
echo.
echo Not: offline_installer klasoru 2-3 GB olabilir.
echo.
pause
