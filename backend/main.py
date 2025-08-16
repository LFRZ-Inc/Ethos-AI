#!/usr/bin/env python3
"""
Ethos AI - Minimal Main
Railway will definitely use this file
"""

import os
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Create FastAPI app
app = FastAPI(title="Ethos AI", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400,
)

@app.get("/")
async def root():
    return {"message": "Ethos AI Backend is running!", "status": "healthy"}

@app.get("/test")
async def test():
    return {"test": "working", "timestamp": time.time()}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "ethos-ai-backend",
        "mode": "minimal",
        "timestamp": time.time(),
        "environment": "production"
    }

@app.get("/api/models")
async def get_models():
    return {
        "models": [
            {
                "id": "ethos-light",
                "name": "Ethos Light",
                "type": "local",
                "provider": "ollama",
                "enabled": True,
                "status": "available",
                "ollama_model": "llama3.2:3b"
            },
            {
                "id": "ethos-code",
                "name": "Ethos Code",
                "type": "local",
                "provider": "ollama",
                "enabled": True,
                "status": "available",
                "ollama_model": "codellama:7b"
            },
            {
                "id": "ethos-pro",
                "name": "Ethos Pro",
                "type": "local",
                "provider": "ollama",
                "enabled": True,
                "status": "available",
                "ollama_model": "gpt-oss:20b"
            },
            {
                "id": "ethos-creative",
                "name": "Ethos Creative",
                "type": "local",
                "provider": "ollama",
                "enabled": True,
                "status": "available",
                "ollama_model": "llama3.1:70b"
            }
        ],
        "total": 4,
        "status": "available",
        "ollama_available": True,
        "ollama_models": ["llama3.2:3b", "codellama:7b", "gpt-oss:20b", "llama3.1:70b"]
    }

@app.get("/api/models/status")
async def get_model_status():
    return {
        "available": True,
        "system_status": {
            "total_models": 4,
            "healthy_models": 4,
            "available_models": ["ethos-light", "ethos-code", "ethos-pro", "ethos-creative"],
            "system_status": "available"
        }
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port) 