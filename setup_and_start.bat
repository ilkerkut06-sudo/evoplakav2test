@echo off
setlocal enabledelayedexpansion

echo ================================================
echo License Plate Recognition System - Setup
echo ================================================
echo.

echo [1/6] Checking Python...
py --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Install from: https://www.python.org/downloads/
    pause
    exit /b 1
)
py --version
echo.

echo [2/6] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found!
    echo Install from: https://nodejs.org/
    pause
    exit /b 1
)
node --version
echo.

echo [3/6] Creating backend virtual environment...
cd /d "%~dp0backend"
if not exist "venv" (
    py -m venv venv
    echo Virtual environment created
)
call venv\Scripts\activate.bat
py -m pip install --upgrade pip
echo.

echo [4/6] Installing backend packages...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Backend packages installation failed!
    pause
    exit /b 1
)
echo Backend packages installed
echo.

echo [5/6] Installing frontend packages...
cd /d "%~dp0frontend"
if not exist "node_modules" (
    npm install
    if errorlevel 1 (
        echo [ERROR] Frontend packages installation failed!
        pause
        exit /b 1
    )
)
echo Frontend packages installed
echo.

echo [6/6] Checking MongoDB...
echo Make sure MongoDB is running on localhost:27017
echo Download from: https://www.mongodb.com/try/download/community
echo.

echo ================================================
echo [SUCCESS] Setup completed!
echo ================================================
echo.
echo Starting servers...
timeout /t 2 >nul

cd /d "%~dp0"
call start_server.bat