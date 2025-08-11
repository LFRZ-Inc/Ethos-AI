@echo off
echo ========================================
echo    ETHOS AI - RAILWAY BACKEND DEPLOYMENT
echo ========================================
echo.

echo This will deploy your Ethos AI backend to Railway (FREE!)
echo Your backend will be accessible from anywhere!
echo.

echo Step 1: Deploy Backend to Railway
echo ---------------------------------
echo 1. Go to: https://railway.app
echo 2. Sign up with GitHub (free)
echo 3. Click "New Project"
echo 4. Select "Deploy from GitHub repo"
echo 5. Choose your Ethos AI repository
echo 6. Configure settings:
echo    - Root Directory: backend
echo    - Start Command: python main.py
echo 7. Wait for deployment (5-10 minutes)
echo.

echo Step 2: Get Your Backend URL
echo -----------------------------
echo Once deployed, Railway will give you a URL like:
echo https://your-app-name.up.railway.app
echo.
echo Copy this URL - you'll need it for the frontend!
echo.

echo Step 3: Deploy Frontend to Vercel
echo ----------------------------------
echo 1. Go to: https://vercel.com
echo 2. Sign up with GitHub (free)
echo 3. Click "New Project"
echo 4. Import your GitHub repository
echo 5. Configure:
echo    - Framework Preset: Vite
echo    - Root Directory: frontend
echo    - Build Command: npm run build
echo    - Output Directory: dist
echo 6. Add Environment Variable:
echo    - Name: VITE_API_BASE_URL
echo    - Value: YOUR_RAILWAY_BACKEND_URL
echo.

echo Step 4: Access from Anywhere!
echo ------------------------------
echo Once both are deployed:
echo - Frontend URL: https://your-app.vercel.app
echo - Works on PC, phone, tablet, anywhere!
echo - No PC required, runs 24/7 in the cloud!
echo.

echo ========================================
echo           DEPLOYMENT COMPLETE!
echo ========================================
echo.
echo Your Ethos AI will be accessible from:
echo - PC: https://your-app.vercel.app
echo - Phone: Same URL!
echo - Anywhere: Same URL!
echo.
echo No more need for PC or WiFi! 🎉
echo.
pause 