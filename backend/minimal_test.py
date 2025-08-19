#!/usr/bin/env python3
"""
Minimal FastAPI test for Railway
VERSION: 1.0.0-MINIMAL-TEST
NO OLLAMA - Just FastAPI
"""

import os
import time
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Initialize FastAPI app
app = FastAPI(title="Ethos AI - Minimal Test", version="1.0.0-MINIMAL-TEST")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple endpoints
@app.get("/")
async def root():
    return {
        "message": "Ethos AI - Minimal Test Working!",
        "status": "healthy",
        "version": "1.0.0-MINIMAL-TEST",
        "deployment": "minimal-test",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0-MINIMAL-TEST",
        "deployment": "minimal-test",
        "message": "FastAPI is working on Railway!"
    }

@app.get("/api/test")
async def api_test():
    return {
        "status": "success",
        "message": "API endpoints are working",
        "deployment": "minimal-test"
    }

# Simple chat mock
class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat")
async def chat_mock(request: ChatRequest):
    return {
        "response": f"Mock response to: {request.message}",
        "model": "mock",
        "deployment": "minimal-test",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
