#!/usr/bin/env python3
"""
Railway startup script for Ethos AI
Handles port configuration and environment setup
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Start the FastAPI application"""
    
    # Get port from Railway environment
    port = int(os.environ.get("PORT", 8000))
    
    # Get host from environment
    host = os.environ.get("HOST", "0.0.0.0")
    
    print(f"Starting Ethos AI on {host}:{port}")
    print(f"Environment: {os.environ.get('RAILWAY_ENVIRONMENT', 'production')}")
    
    # Import and start the FastAPI app from railway-main.py
    try:
        from railway_main import app
        
        # Start the server
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"Error importing app: {e}")
        print("Make sure all dependencies are installed")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 