@echo off
echo ========================================
echo        ETHOS AI - RENDER DEPLOYMENT
echo ========================================
echo.

echo Render is MORE RELIABLE than Railway and Vercel!
echo.

echo Step 1: Deploy Backend to Render
echo --------------------------------
echo 1. Go to: https://render.com
echo 2. Sign up with GitHub (free)
echo 3. Click "New +" → "Web Service"
echo 4. Connect your GitHub repository
echo 5. Configure:
echo    - Name: ethos-ai-backend
echo    - Environment: Python 3
echo    - Build Command: pip install -r backend/requirements.txt
echo    - Start Command: cd backend && python main.py
echo    - Plan: Free
echo 6. Click "Create Web Service"
echo 7. Wait 5-10 minutes
echo 8. Copy your backend URL
echo.

echo Step 2: Deploy Frontend to Render
echo ---------------------------------
echo 1. Click "New +" → "Static Site"
echo 2. Connect your GitHub repository
echo 3. Configure:
echo    - Name: ethos-ai-frontend
echo    - Build Command: cd frontend && npm install && npm run build
echo    - Publish Directory: frontend/dist
echo    - Plan: Free
echo 4. Add Environment Variable:
echo    - Name: VITE_API_BASE_URL
echo    - Value: YOUR_BACKEND_URL (from Step 1)
echo 5. Click "Create Static Site"
echo 6. Wait 3-5 minutes
echo.

echo Step 3: Access from Anywhere!
echo -----------------------------
echo Once deployed, you'll get URLs like:
echo - Frontend: https://ethos-ai-frontend.onrender.com
echo - Backend: https://ethos-ai-backend.onrender.com
echo.
echo Access from PC, phone, tablet, anywhere!
echo.

echo ========================================
echo           DEPLOYMENT COMPLETE!
echo ========================================
echo.
echo Your Ethos AI will be accessible from:
echo - PC: https://ethos-ai-frontend.onrender.com
echo - Phone: Same URL!
echo - Anywhere: Same URL!
echo.
echo No more need for PC or WiFi! 🎉
echo.
pause 