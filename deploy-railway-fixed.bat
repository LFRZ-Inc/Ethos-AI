@echo off
echo ========================================
echo Ethos AI - Railway Deployment (Fixed)
echo ========================================
echo.

echo [1/5] Checking Railway CLI...
railway --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Railway CLI not found. Please install it first:
    echo npm install -g @railway/cli
    pause
    exit /b 1
)

echo [2/5] Checking if logged into Railway...
railway whoami >nul 2>&1
if %errorlevel% neq 0 (
    echo Please log into Railway first:
    railway login
    pause
    exit /b 1
)

echo [3/5] Switching to backend directory...
cd backend

echo [4/5] Deploying to Railway...
echo Using simplified railway-main.py for reliable deployment...
railway up

echo [5/5] Deployment complete!
echo.
echo Your Ethos AI backend should now be available at:
echo https://ethos-ai-backend-production.up.railway.app
echo.
echo Test the health endpoint:
echo https://ethos-ai-backend-production.up.railway.app/health
echo.
echo Test the chat endpoint:
echo https://ethos-ai-backend-production.up.railway.app/api/chat
echo.
pause
