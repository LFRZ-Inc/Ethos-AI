@echo off
REM Ethos AI Installation Script for Windows
REM This script sets up the complete Ethos AI environment

echo 🚀 Installing Ethos AI...

REM Check Python version
echo [INFO] Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed. Please install Python 3.11+ first.
    pause
    exit /b 1
)

REM Check Node.js version
echo [INFO] Checking Node.js version...
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed. Please install Node.js 18+ first.
    pause
    exit /b 1
)

echo [SUCCESS] Prerequisites check passed

REM Install Python dependencies
echo [INFO] Installing Python dependencies...
cd backend
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cd ..
echo [SUCCESS] Python dependencies installed

REM Install Node.js dependencies
echo [INFO] Installing Node.js dependencies...
cd frontend
npm install
cd ..
echo [SUCCESS] Node.js dependencies installed

REM Create data directories
echo [INFO] Creating data directories...
if not exist "%USERPROFILE%\EthosAIData" mkdir "%USERPROFILE%\EthosAIData"
if not exist "%USERPROFILE%\EthosAIData\conversations" mkdir "%USERPROFILE%\EthosAIData\conversations"
if not exist "%USERPROFILE%\EthosAIData\embeddings" mkdir "%USERPROFILE%\EthosAIData\embeddings"
if not exist "%USERPROFILE%\EthosAIData\models" mkdir "%USERPROFILE%\EthosAIData\models"
if not exist "%USERPROFILE%\EthosAIData\uploads" mkdir "%USERPROFILE%\EthosAIData\uploads"
if not exist "%USERPROFILE%\EthosAIData\exports" mkdir "%USERPROFILE%\EthosAIData\exports"
if not exist "%USERPROFILE%\EthosAIData\logs" mkdir "%USERPROFILE%\EthosAIData\logs"
echo [SUCCESS] Data directories created

REM Create configuration
echo [INFO] Setting up configuration...
if not exist "%USERPROFILE%\.ethos_ai\config" mkdir "%USERPROFILE%\.ethos_ai\config"
if not exist "%USERPROFILE%\.ethos_ai\config\config.yaml" (
    copy "backend\config\config.example.yaml" "%USERPROFILE%\.ethos_ai\config\config.yaml" >nul 2>&1
    echo [SUCCESS] Configuration file created at %USERPROFILE%\.ethos_ai\config\config.yaml
) else (
    echo [SUCCESS] Configuration file already exists
)

echo.
echo [SUCCESS] 🎉 Ethos AI installation completed!
echo.
echo [INFO] Next steps:
echo 1. Edit %USERPROFILE%\.ethos_ai\config\config.yaml to add your API keys
echo 2. Run 'scripts\start.bat' to start the application
echo 3. Open http://localhost:1420 in your browser
echo.
echo [INFO] For more information, see the README.md file
pause 