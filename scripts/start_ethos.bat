@echo off
echo Starting Ethos AI...
echo.

REM Get the current directory
set "CURRENT_DIR=%~dp0"
set "BACKEND_DIR=%CURRENT_DIR%..\backend"
set "FRONTEND_DIR=%CURRENT_DIR%..\frontend"

echo Backend directory: %BACKEND_DIR%
echo Frontend directory: %FRONTEND_DIR%
echo.

REM Start Backend in background
echo Starting Backend Server...
start "Ethos AI Backend" /min cmd /c "cd /d %BACKEND_DIR% && python main.py"

REM Wait a moment for backend to start
timeout /t 10 /nobreak > nul

REM Start Frontend in background
echo Starting Frontend Server...
start "Ethos AI Frontend" /min cmd /c "cd /d %FRONTEND_DIR% && npm run dev"

echo.
echo Ethos AI is starting up...
echo Backend: http://localhost:8003
echo Frontend: http://localhost:5173
echo.
echo Services are running in the background.
echo To stop them, close the minimized command windows.
echo.
pause 