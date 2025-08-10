@echo off
REM Ethos AI Startup Script for Windows
REM This script starts both the backend and frontend

echo [INFO] Starting Ethos AI...

REM Check if we're in the right directory
if not exist "backend\main.py" (
    echo [ERROR] Please run this script from the Ethos AI root directory
    pause
    exit /b 1
)

if not exist "frontend\package.json" (
    echo [ERROR] Please run this script from the Ethos AI root directory
    pause
    exit /b 1
)

REM Start backend
echo [INFO] Starting backend server...
cd backend
start "Ethos AI Backend" python main.py
cd ..

REM Wait for backend to start
timeout /t 3 /nobreak >nul

REM Check if backend is running
curl -s http://localhost:8000/ >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Backend may not be ready yet
) else (
    echo [SUCCESS] Backend started successfully
)

REM Start frontend
echo [INFO] Starting frontend...
cd frontend
start "Ethos AI Frontend" npm run dev
cd ..

REM Wait for frontend to start
timeout /t 5 /nobreak >nul

REM Check if frontend is running
curl -s http://localhost:1420 >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Frontend may not be ready yet
) else (
    echo [SUCCESS] Frontend started successfully
)

echo.
echo [SUCCESS] 🎉 Ethos AI is now running!
echo.
echo [INFO] Access the application at:
echo   Frontend: http://localhost:1420
echo   Backend API: http://localhost:8000
echo.
echo [INFO] Press any key to stop the application
pause

REM Cleanup - stop the processes
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
echo [INFO] Application stopped 