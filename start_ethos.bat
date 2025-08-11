@echo off
echo ========================================
echo           ETHOS AI STARTUP
echo ========================================
echo.

REM Get the current directory
set "CURRENT_DIR=%~dp0"
set "BACKEND_DIR=%CURRENT_DIR%backend"
set "FRONTEND_DIR=%CURRENT_DIR%frontend"

echo Starting Ethos AI...
echo Backend: %BACKEND_DIR%
echo Frontend: %FRONTEND_DIR%
echo.

REM Get local IP address
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set "LOCAL_IP=%%a"
    set "LOCAL_IP=!LOCAL_IP: =!"
    goto :found_ip
)
:found_ip

echo Your local IP: %LOCAL_IP%
echo.

REM Start Backend
echo [1/2] Starting Backend Server...
start "Ethos AI Backend" /min cmd /c "cd /d %BACKEND_DIR% && python main.py"

REM Wait for backend
echo Waiting for backend to initialize...
timeout /t 20 /nobreak > nul

REM Start Frontend
echo [2/2] Starting Frontend Server...
start "Ethos AI Frontend" /min cmd /c "cd /d %FRONTEND_DIR% && npm run dev"

echo.
echo ========================================
echo           ETHOS AI READY!
echo ========================================
echo.
echo Access from PC:     http://localhost:1420
echo Access from Phone:  http://%LOCAL_IP%:1420
echo.
echo Make sure your phone is on the same WiFi!
echo.
echo Services are running in background.
echo To stop: Close the minimized command windows.
echo.
echo Press any key to exit...
pause > nul 