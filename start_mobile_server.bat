@echo off
echo.
echo ========================================
echo    Ethos AI - Mobile Server
echo ========================================
echo.

cd backend

echo Starting Ethos AI Mobile Server...
echo.
echo This will make Ethos AI accessible from:
echo - Your phone (same WiFi)
echo - Any device on your network
echo - No internet required!
echo.

python local_network_server.py

pause
