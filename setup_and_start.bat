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

REM Create .env for backend if not exists
if not exist ".env" (
    echo Creating backend .env file...
    (
        echo MONGO_URL=mongodb://localhost:27017
        echo DB_NAME=test_database
        echo CORS_ORIGINS=*
    ) > .env
    echo Backend .env created
)

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

REM Create .env.local for local backend connection
if not exist ".env.local" (
    echo Creating .env.local for local development...
    echo REACT_APP_BACKEND_URL=http://localhost:8001 > .env.local
    echo .env.local created
)

REM Check if craco exists (critical dependency)
set NEED_INSTALL=0

if not exist "node_modules" (
    echo node_modules not found, will install...
    set NEED_INSTALL=1
) else (
    echo Checking for craco...
    if not exist "node_modules\.bin\craco.cmd" (
        echo craco not found, will reinstall packages...
        set NEED_INSTALL=1
    ) else (
        echo craco found, packages OK
    )
)

if %NEED_INSTALL%==1 (
    echo Installing frontend packages...
    where yarn >nul 2>&1
    if errorlevel 1 (
        echo Using npm with --legacy-peer-deps...
        call npm install --legacy-peer-deps
    ) else (
        echo Using Yarn...
        call yarn install
    )
    if errorlevel 1 (
        echo [ERROR] Frontend packages installation failed!
        pause
        exit /b 1
    )
    echo Frontend packages installed successfully
)
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