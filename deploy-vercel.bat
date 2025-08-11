@echo off
echo ========================================
echo        ETHOS AI - VERCEL DEPLOYMENT
echo ========================================
echo.

echo Step 1: Deploy Backend First
echo -----------------------------
echo You need to deploy your backend to Railway, Render, or Fly.io
echo.
echo Recommended: Railway (easiest)
echo 1. Go to: https://railway.app
echo 2. Sign up with GitHub
echo 3. Deploy your backend
echo 4. Get your backend URL
echo.

echo Step 2: Push to GitHub
echo ----------------------
echo This will push your code to GitHub for Vercel deployment
echo.
git add .
git commit -m "Deploy to Vercel - Ethos AI"
git push origin main
echo.

echo Step 3: Deploy to Vercel
echo ------------------------
echo 1. Go to: https://vercel.com
echo 2. Sign up/Login with GitHub
echo 3. Click "New Project"
echo 4. Import your GitHub repository
echo 5. Configure:
echo    - Framework Preset: Vite
echo    - Root Directory: frontend
echo    - Build Command: npm run build
echo    - Output Directory: dist
echo.

echo Step 4: Set Environment Variable
echo --------------------------------
echo In Vercel dashboard, add environment variable:
echo VITE_API_BASE_URL=https://your-backend-url.com
echo (Replace with your actual backend URL)
echo.

echo Step 5: Access Your Ethos AI
echo ----------------------------
echo Once deployed, you'll get a URL like:
echo https://your-ethos-ai.vercel.app
echo.
echo This will work on PC, phone, tablet, anywhere!
echo.

echo ========================================
echo           DEPLOYMENT COMPLETE!
echo ========================================
echo.
echo Your Ethos AI will be accessible from:
echo - PC: https://your-ethos-ai.vercel.app
echo - Phone: Same URL!
echo - Anywhere: Same URL!
echo.
echo No more need to keep your PC running! 🎉
echo.
pause 