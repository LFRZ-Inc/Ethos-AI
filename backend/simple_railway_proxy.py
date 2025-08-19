"""
Simple Railway Proxy for Ethos AI
Simplified version for Railway deployment
"""
import os
import requests
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Ethos AI - Railway Proxy", version="5.4.0-SIMPLE")

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
    """Root endpoint"""
    return {
        "message": "Ethos AI - Railway Proxy",
        "status": "active",
        "localtunnel_url": LOCALTUNNEL_URL,
        "version": "5.4.0-SIMPLE"
    }

@app.get("/health")
async def health():
    """Health check - proxy to LocalTunnel"""
    try:
        response = requests.get(f"{LOCALTUNNEL_URL}/health", timeout=10)
        return JSONResponse(content=response.json(), status_code=response.status_code)
    except Exception as e:
        return JSONResponse(
            content={
                "status": "unhealthy",
                "error": str(e),
                "localtunnel_url": LOCALTUNNEL_URL
            },
            status_code=503
        )

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
async def proxy_request(request: Request, path: str):
    """Proxy all API requests to LocalTunnel"""
    try:
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
            status_code=response.status_code
        )
        
    except Exception as e:
        return JSONResponse(
            content={"error": f"Proxy error: {str(e)}"},
            status_code=500
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
