@echo off
echo ========================================
echo ETHOS AI - STOPPING PRODUCTION SERVICES
echo ========================================
echo.

echo [1/3] Stopping Python processes...
taskkill /f /im python.exe >nul 2>&1
echo ✅ Python processes stopped

echo.
echo [2/3] Stopping Node.js processes...
taskkill /f /im node.exe >nul 2>&1
echo ✅ Node.js processes stopped

echo.
echo [3/3] Checking for remaining processes...
netstat -ano | findstr :8000 >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠️  Port 8000 still in use
) else (
    echo ✅ Port 8000 is free
)

netstat -ano | findstr :1420 >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠️  Port 1420 still in use
) else (
    echo ✅ Port 1420 is free
)

echo.
echo ========================================
echo ✅ ALL ETHOS AI SERVICES STOPPED
echo ========================================
echo.
pause
