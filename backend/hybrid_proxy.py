"""
Hybrid Proxy for Ethos AI
Railway -> LocalTunnel Proxy
"""
import os
import requests
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Ethos AI - Hybrid Proxy",
    description="Railway proxy to LocalTunnel backend",
    version="5.4.0-HYBRID-PROXY"
)

# LocalTunnel backend URL
LOCALTUNNEL_URL = "https://ethos-ai-test.loca.lt"

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint - proxy to LocalTunnel"""
    try:
        response = requests.get(f"{LOCALTUNNEL_URL}/", timeout=10)
        return JSONResponse(
            content=response.json(),
            status_code=response.status_code,
            headers=dict(response.headers)
        )
    except Exception as e:
        logger.error(f"Proxy error: {e}")
        return JSONResponse(
            content={
                "message": "Ethos AI - Hybrid Proxy",
                "status": "proxy_active",
                "localtunnel_url": LOCALTUNNEL_URL,
                "error": "LocalTunnel connection failed - ensure LocalTunnel is running"
            },
            status_code=503
        )

@app.get("/health")
async def health():
    """Health check - proxy to LocalTunnel"""
    try:
        response = requests.get(f"{LOCALTUNNEL_URL}/health", timeout=10)
        return JSONResponse(
            content=response.json(),
            status_code=response.status_code,
            headers=dict(response.headers)
        )
    except Exception as e:
        logger.error(f"Health proxy error: {e}")
        return JSONResponse(
            content={
                "status": "unhealthy",
                "error": "LocalTunnel connection failed",
                "localtunnel_url": LOCALTUNNEL_URL
            },
            status_code=503
        )

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
async def proxy_request(request: Request, path: str):
    """Proxy all API requests to LocalTunnel"""
    try:
        # Build the target URL
        target_url = f"{LOCALTUNNEL_URL}/{path}"
        
        # Get request body
        body = None
        if request.method in ["POST", "PUT"]:
            body = await request.body()
        
        # Forward the request
        response = requests.request(
            method=request.method,
            url=target_url,
            headers=dict(request.headers),
            params=dict(request.query_params),
            data=body,
            timeout=30
        )
        
        # Return the response
        return JSONResponse(
            content=response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
            status_code=response.status_code,
            headers=dict(response.headers)
        )
        
    except requests.exceptions.Timeout:
        logger.error(f"Timeout proxying to {target_url}")
        raise HTTPException(status_code=504, detail="LocalTunnel timeout")
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error to {target_url}")
        raise HTTPException(status_code=503, detail="LocalTunnel connection failed")
    except Exception as e:
        logger.error(f"Proxy error: {e}")
        raise HTTPException(status_code=500, detail=f"Proxy error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

# Railway-specific startup for Procfile compatibility
# This ensures the app starts properly on Railway
app.debug = False
