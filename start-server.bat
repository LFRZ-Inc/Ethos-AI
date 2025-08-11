@echo off
echo ========================================
echo        ETHOS AI - SERVER STARTUP
echo ========================================
echo.

echo Starting Ethos AI on your PC...
echo.

echo Step 1: Starting Backend Server...
echo ---------------------------------
start "Ethos AI Backend" cmd /k "cd backend && python main.py"

echo Waiting for backend to start...
timeout /t 10 /nobreak > nul

echo Step 2: Starting Frontend Server...
echo ----------------------------------
start "Ethos AI Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo           SERVER STARTED!
echo ========================================
echo.
echo Your Ethos AI is now running on:
echo.
echo PC Access:     http://localhost:1420
echo.
echo To access from your phone:
echo 1. Find your PC's IP address
echo 2. Access: http://YOUR_PC_IP:1420
echo.
echo To find your PC's IP:
echo - Press Win+R, type "cmd", press Enter
echo - Type "ipconfig" and press Enter
echo - Look for "IPv4 Address" (usually 192.168.x.x)
echo.
echo ========================================
echo.
pause 