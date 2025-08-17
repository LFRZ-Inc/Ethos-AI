@echo off
echo 🌐 Starting Ethos AI Tunnel...
echo.

REM Check if npx is available
where npx >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ npx not found. Please install Node.js first.
    pause
    exit /b 1
)

REM Check if Ollama is running
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Ollama not running. Please start Ollama first.
    echo Run: ollama serve
    pause
    exit /b 1
)

echo ✅ Ollama is running
echo 🚀 Starting tunnel...

REM Start localtunnel
npx localtunnel --port 11434 --subdomain ethos-ollama

echo.
echo If successful, your tunnel URL will be: https://ethos-ollama.loca.lt
echo.
pause
