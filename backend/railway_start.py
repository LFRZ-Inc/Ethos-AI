#!/usr/bin/env python3
"""
Minimal Railway Backend - Guaranteed to work
"""

import os
import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Create FastAPI app
app = FastAPI(title="Ethos AI", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    content: str = ""
    message: str = ""
    conversation_id: str = None
    model_override: str = None

# Simple models
MODELS = {
    "ethos-simple": {
        "id": "ethos-simple",
        "name": "Ethos Simple AI",
        "status": "available",
        "description": "Simple AI for basic conversations"
    }
}

@app.get("/")
async def root():
    return {
        "message": "Ethos AI Backend is running!",
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": time.time()
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "ethos-ai-backend",
        "timestamp": time.time()
    }

@app.get("/test")
async def test():
    return {
        "status": "ok",
        "message": "Backend is working",
        "timestamp": time.time()
    }

@app.get("/api/models")
async def get_models():
    return {
        "models": list(MODELS.values()),
        "total": len(MODELS),
        "status": "available"
    }

@app.get("/api/models/status")
async def get_model_status():
    return {
        "status": "available",
        "models_loaded": len(MODELS),
        "total_models": len(MODELS),
        "system_healthy": True,
        "timestamp": time.time()
    }

@app.post("/api/chat")
async def chat(message: ChatMessage):
    content = message.content or message.message or "Hello"
    
    # Simple response logic
    if "hello" in content.lower() or "hi" in content.lower():
        response = "Hello! I'm Ethos AI, your privacy-focused assistant. I'm running in simplified mode and can help you with basic tasks."
    elif "?" in content:
        response = f"That's an interesting question about {content}! I'm currently running in simplified mode for reliable deployment. How can I help you?"
    else:
        response = f"I understand you're asking about {content}. I'm running in simplified mode and can provide basic assistance. What would you like help with?"
    
    return {
        "content": response,
        "model_used": "ethos-simple",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "tools_called": []
    }

@app.get("/api/conversations")
async def get_conversations():
    return {
        "conversations": [],
        "total": 0
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
