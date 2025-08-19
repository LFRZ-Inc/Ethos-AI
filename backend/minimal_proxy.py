"""
Minimal Railway Proxy for Ethos AI
Ultra-simplified version for Railway deployment
"""
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)

# Add CORS support
CORS(app, origins=["*"], allow_headers=["*"], methods=["*"])

# LocalTunnel backend URL
LOCALTUNNEL_URL = "https://ethos-ai-test.loca.lt"

@app.route('/')
def root():
    """Root endpoint"""
    try:
        response = requests.get(f"{LOCALTUNNEL_URL}/", timeout=10)
        return response.json(), response.status_code
    except Exception as e:
        return {
            "message": "Ethos AI - Railway Proxy",
            "status": "proxy_active",
            "localtunnel_url": LOCALTUNNEL_URL,
            "error": "LocalTunnel connection failed - ensure LocalTunnel is running"
        }, 503

@app.route('/health')
def health():
    """Health check - proxy to LocalTunnel"""
    try:
        response = requests.get(f"{LOCALTUNNEL_URL}/health", timeout=10)
        return response.json(), response.status_code
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": "LocalTunnel connection failed",
            "localtunnel_url": LOCALTUNNEL_URL
        }, 503

@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def proxy_request(path):
    """Proxy all API requests to LocalTunnel"""
    try:
        # Clean the path to avoid double slashes
        clean_path = path.lstrip('/')
        target_url = f"{LOCALTUNNEL_URL}/{clean_path}"
        
        # Get request body
        body = None
        if request.method in ["POST", "PUT"]:
            body = request.get_data()
        
        # Forward the request
        response = requests.request(
            method=request.method,
            url=target_url,
            headers=dict(request.headers),
            params=dict(request.args),
            data=body,
            timeout=30
        )
        
        # Return the response
        return response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text, response.status_code
        
    except Exception as e:
        return {"error": f"Proxy error: {str(e)}"}, 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
