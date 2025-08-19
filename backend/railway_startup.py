"""
Railway Startup Script for Ethos AI Hybrid Proxy
This ensures proper startup on Railway platform
"""
import os
import sys
from hybrid_proxy import app

if __name__ == "__main__":
    # Railway environment setup
    port = int(os.environ.get("PORT", 8000))
    
    # Import and run the hybrid proxy app
    import uvicorn
    uvicorn.run(
        "hybrid_proxy:app",
        host="0.0.0.0",
        port=port,
        workers=1,
        timeout_keep_alive=600
    )
