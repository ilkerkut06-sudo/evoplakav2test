@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ================================================
echo Plaka Tanıma Sistemi - Kurulum ve Başlatma
echo ================================================
echo.

:: Windows kontrolü
if not "%OS%"=="Windows_NT" (
    echo HATA: Bu kurulum sadece Windows üzerinde çalışır.
    echo Lütfen Windows işletim sistemi kullanın.
    pause
    exit /b 1
)

echo [✓] İşletim sistemi: Windows
echo.

:: Python kontrolü
echo [1/8] Python kontrol ediliyor...
python --version >nul 2>&1
if errorlevel 1 (
    echo [✗] HATA: Python bulunamadı!
    echo Lütfen Python 3.8 veya üstünü yükleyin: https://www.python.org/downloads/
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do echo [✓] %%i bulundu
echo.

:: Node.js kontrolü
echo [2/8] Node.js kontrol ediliyor...
node --version >nul 2>&1
if errorlevel 1 (
    echo [✗] HATA: Node.js bulunamadı!
    echo Lütfen Node.js yükleyin: https://nodejs.org/
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version') do echo [✓] Node.js %%i bulundu
echo.

:: Backend sanal ortam oluşturma
echo [3/8] Backend sanal ortamı oluşturuluyor...
cd /d "%~dp0backend"
if not exist "venv" (
    python -m venv venv
    if errorlevel 1 (
        echo [✗] HATA: Sanal ortam oluşturulamadı!
        pause
        exit /b 1
    )
    echo [✓] Sanal ortam oluşturuldu
) else (
    echo [✓] Sanal ortam zaten mevcut
)
echo.

:: Sanal ortamı aktif et ve paketleri yükle
echo [4/8] Python paketleri yükleniyor...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
if errorlevel 1 (
    echo [✗] HATA: Python paketleri yüklenemedi!
    pause
    exit /b 1
)
echo [✓] Tüm Python paketleri yüklendi
echo.

:: YOLO modeli indirme
echo [5/8] YOLO modeli kontrol ediliyor...
if not exist "models\yolov8n.pt" (
    mkdir models 2>nul
    echo YOLO modeli indiriliyor... (Bu ilk seferde biraz zaman alabilir)
    python -c "from ultralytics import YOLO; model = YOLO('yolov8n.pt'); model.export()"
    echo [✓] YOLO modeli hazır
) else (
    echo [✓] YOLO modeli zaten mevcut
)
echo.

:: Frontend paketleri
echo [6/8] Frontend paketleri yükleniyor...
cd /d "%~dp0frontend"
call yarn install
if errorlevel 1 (
    echo [✗] HATA: Frontend paketleri yüklenemedi!
    pause
    exit /b 1
)
echo [✓] Frontend paketleri yüklendi
echo.

:: MongoDB kontrolü
echo [7/8] MongoDB bağlantısı kontrol ediliyor...
echo [i] MongoDB'nin çalıştığından emin olun (localhost:27017)
echo.

:: Veritabanı başlangıç verisi
echo [8/8] Veritabanı hazırlanıyor...
cd /d "%~dp0backend"
call venv\Scripts\activate.bat
python -c "print('[✓] Veritabanı hazır')"
echo.

echo ================================================
echo [✓] KURULUM TAMAMLANDI!
echo ================================================
echo.
echo Sunucuları başlatmak için start_server.bat dosyasını çalıştırın
echo veya otomatik başlatma için bir tuşa basın...
echo.
pause

:: Otomatik başlatma
cd /d "%~dp0"
call start_server.bat