@echo off
echo Starting Ethos AI with Network Access...
echo.

REM Get the current directory
set "CURRENT_DIR=%~dp0"
set "BACKEND_DIR=%CURRENT_DIR%..\backend"
set "FRONTEND_DIR=%CURRENT_DIR%..\frontend"

echo Backend directory: %BACKEND_DIR%
echo Frontend directory: %FRONTEND_DIR%
echo.

REM Get local IP address
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set "LOCAL_IP=%%a"
    set "LOCAL_IP=!LOCAL_IP: =!"
    goto :found_ip
)
:found_ip

echo Your local IP address: %LOCAL_IP%
echo.

REM Start Backend with network access
echo Starting Backend Server with network access...
start "Ethos AI Backend" /min cmd /c "cd /d %BACKEND_DIR% && uvicorn main:app --host 0.0.0.0 --port 8003"

REM Wait for backend to start
echo Waiting for backend to start...
timeout /t 15 /nobreak > nul

REM Start Frontend with network access
echo Starting Frontend Server with network access...
start "Ethos AI Frontend" /min cmd /c "cd /d %FRONTEND_DIR% && npm run dev -- --host 0.0.0.0"

echo.
echo ========================================
echo Ethos AI is now accessible from:
echo.
echo PC: http://localhost:5173
echo Phone: http://%LOCAL_IP%:5173
echo Backend: http://%LOCAL_IP%:8003
echo.
echo Make sure your phone is on the same WiFi network!
echo.
echo To access from phone:
echo 1. Connect your phone to the same WiFi
echo 2. Open browser on phone
echo 3. Go to: http://%LOCAL_IP%:5173
echo.
echo ========================================
echo.
pause 