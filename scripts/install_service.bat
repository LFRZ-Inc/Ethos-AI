@echo off
echo Installing Ethos AI as Windows Service...

REM Get the current directory
set "CURRENT_DIR=%~dp0"
set "BACKEND_DIR=%CURRENT_DIR%..\backend"
set "FRONTEND_DIR=%CURRENT_DIR%..\frontend"

REM Install NSSM (Non-Sucking Service Manager) if not already installed
if not exist "C:\nssm\nssm.exe" (
    echo Downloading NSSM...
    powershell -Command "Invoke-WebRequest -Uri 'https://nssm.cc/release/nssm-2.24.zip' -OutFile 'nssm.zip'"
    powershell -Command "Expand-Archive -Path 'nssm.zip' -DestinationPath 'C:\nssm' -Force"
    del nssm.zip
)

REM Install Backend Service
echo Installing Backend Service...
C:\nssm\nssm.exe install "EthosAIBackend" "C:\Python\python.exe" "main.py"
C:\nssm\nssm.exe set "EthosAIBackend" AppDirectory "%BACKEND_DIR%"
C:\nssm\nssm.exe set "EthosAIBackend" Description "Ethos AI Backend Server"
C:\nssm\nssm.exe set "EthosAIBackend" Start SERVICE_AUTO_START

REM Install Frontend Service
echo Installing Frontend Service...
C:\nssm\nssm.exe install "EthosAIFrontend" "C:\Program Files\nodejs\npm.cmd" "run dev"
C:\nssm\nssm.exe set "EthosAIFrontend" AppDirectory "%FRONTEND_DIR%"
C:\nssm\nssm.exe set "EthosAIFrontend" Description "Ethos AI Frontend Server"
C:\nssm\nssm.exe set "EthosAIFrontend" Start SERVICE_AUTO_START

REM Start the services
echo Starting services...
net start "EthosAIBackend"
net start "EthosAIFrontend"

echo.
echo Ethos AI services installed and started!
echo Backend: http://localhost:8003
echo Frontend: http://localhost:5173
echo.
echo To manage services:
echo - Start: net start EthosAIBackend
echo - Stop: net stop EthosAIBackend
echo - Status: sc query EthosAIBackend
echo.
pause 