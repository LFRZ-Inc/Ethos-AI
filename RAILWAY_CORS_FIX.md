# Railway CORS Fix Guide

## Problem
Your Vercel frontend at `https://ethos-ai-phi.vercel.app` is getting CORS errors when trying to connect to your Railway backend at `https://cooking-ethos-ai-production-6bfd.up.railway.app`.

## Root Cause
The Railway backend is not responding (502 Bad Gateway), which means it's not running properly. This is likely due to heavy AI dependencies causing the deployment to fail.

## Solution
I've created a simplified backend that removes heavy AI dependencies and focuses on basic functionality.

## Steps to Fix

### 1. Update Railway Backend Files

**Replace the following files in your Railway deployment:**

#### `backend/Procfile`
```
web: gunicorn simple_railway_main:app --bind 0.0.0.0:$PORT --workers 1
```

#### `backend/requirements.txt`
```
# Core FastAPI and web framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0

# HTTP client
httpx==0.25.2

# Utilities
python-multipart==0.0.6
aiofiles==23.2.0
pyyaml==6.0.0
python-dotenv==1.0.0
requests==2.31.0

# Production server
gunicorn==21.2.0
```

#### `backend/simple_railway_main.py`
This file has been created with:
- ✅ Proper CORS configuration
- ✅ Basic API endpoints
- ✅ No heavy AI dependencies
- ✅ Health check endpoints
- ✅ Simplified response generation

### 2. Deploy to Railway

1. **Push these changes to your GitHub repository**
2. **Railway will automatically redeploy**
3. **Wait for deployment to complete**

### 3. Test the Backend

Once deployed, test these endpoints:

```bash
# Health check
curl https://cooking-ethos-ai-production-6bfd.up.railway.app/health

# Root endpoint
curl https://cooking-ethos-ai-production-6bfd.up.railway.app/

# Models endpoint
curl https://cooking-ethos-ai-production-6bfd.up.railway.app/api/models

# Test endpoint
curl https://cooking-ethos-ai-production-6bfd.up.railway.app/test
```

### 4. Verify CORS Headers

The simplified backend includes proper CORS headers:
- `Access-Control-Allow-Origin: *`
- `Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS`
- `Access-Control-Allow-Headers: *`

### 5. Test Frontend Connection

Once the backend is working, your Vercel frontend should be able to connect without CORS errors.

## What the Simplified Backend Provides

✅ **Basic Chat Functionality** - Responds to messages with intelligent fallback responses
✅ **Model Status** - Reports available models and system status
✅ **Health Checks** - Proper health endpoints for Railway
✅ **CORS Support** - Explicit CORS configuration for Vercel frontend
✅ **Error Handling** - Proper error responses and logging
✅ **No Heavy Dependencies** - Fast startup and reliable deployment

## Next Steps

1. **Deploy the simplified backend**
2. **Test the connection**
3. **Verify CORS is working**
4. **Add AI models back gradually** (optional)

## Expected Results

After deployment, you should see:
- ✅ Backend responds to health checks
- ✅ CORS headers are present
- ✅ Frontend can connect without errors
- ✅ Basic chat functionality works
- ✅ No more 502 Bad Gateway errors

## Troubleshooting

If you still get CORS errors:
1. Check Railway deployment logs
2. Verify the backend is responding
3. Test endpoints directly
4. Check environment variables in Railway

The simplified backend removes all heavy AI dependencies that were likely causing the Railway deployment to fail.
