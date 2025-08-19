@echo off
echo ========================================
echo ETHOS AI - PRODUCTION STARTUP
echo ========================================
echo.

echo [1/4] Checking Ollama availability...
ollama --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Ollama not found! Please install Ollama first.
    echo Download from: https://ollama.ai
    pause
    exit /b 1
)
echo ✅ Ollama is available

echo.
echo [2/4] Starting Backend Server...
cd backend
start "Ethos AI Backend" /min python client_storage_version.py
timeout /t 3 /nobreak >nul

echo.
echo [3/4] Starting Frontend Server...
cd ..\frontend
start "Ethos AI Frontend" /min npm run dev
timeout /t 5 /nobreak >nul

echo.
echo [4/4] Starting LocalTunnel...
cd ..
start "Ethos AI Tunnel" /min lt --port 8000 --subdomain ethos-ai-test
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo 🎉 ETHOS AI PRODUCTION READY!
echo ========================================
echo.
echo 📱 Frontend: http://localhost:1420
echo 🔧 Backend:  http://127.0.0.1:8000
echo 🌍 Remote:   https://ethos-ai-test.loca.lt
echo.
echo 💡 To stop all services, run: stop_production.bat
echo.
pause
