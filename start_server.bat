@echo off

echo ================================================
echo Starting License Plate Recognition System
echo ================================================
echo.

echo Starting Backend on port 8001...
start "Backend Server" cmd /k "cd /d %~dp0backend && call venv\Scripts\activate.bat && py -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload"

timeout /t 3 >nul

echo Starting Frontend on port 3000...
start "Frontend Server" cmd /k "cd /d %~dp0frontend && set PORT=3000 && yarn start"

timeout /t 5 >nul

echo.
echo Opening browser...
start http://localhost:3000

echo.
echo ================================================
echo [SUCCESS] All servers running!
echo ================================================
echo.
echo Backend: http://localhost:8001
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8001/docs
echo.
echo Close the server windows to stop.
pause