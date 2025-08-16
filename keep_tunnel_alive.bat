@echo off
echo 🚀 Ethos AI Tunnel Manager
echo =========================
echo This script keeps your localtunnel running for Ethos AI
echo Press Ctrl+C to stop
echo.

:start
echo 📡 Starting localtunnel...
lt --port 11434 --subdomain ethos-ollama

echo.
echo ⚠️  Tunnel stopped. Restarting in 5 seconds...
timeout /t 5 /nobreak >nul
goto start
