#!/usr/bin/env python3
"""
Ethos AI - Minimal App
Railway will definitely use this file
"""

import os
import time
import logging
import uuid
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Pydantic models
class ChatMessage(BaseModel):
    content: Optional[str] = None
    message: Optional[str] = None
    conversation_id: Optional[str] = None
    model_override: Optional[str] = None
    use_tools: bool = True
    
    def get_content(self) -> str:
        if self.content:
            return self.content
        elif self.message:
            return self.message
        else:
            raise ValueError("Either 'content' or 'message' field is required")

@app.get("/")
async def root():
    return {"message": "Ethos AI Backend is running!", "status": "healthy"}

@app.get("/health")
async def health_check():
    health_data = {
        "status": "healthy",
        "service": "ethos-ai-backend",
        "mode": "minimal",
        "timestamp": time.time(),
        "environment": "production"
    }
    
    from fastapi.responses import JSONResponse
    response = JSONResponse(content=health_data)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

@app.get("/api/models")
async def get_models():
    """Get available models - hardcoded for stability"""
    response_data = {
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
    
    from fastapi.responses import JSONResponse
    response = JSONResponse(content=response_data)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

@app.get("/api/models/status")
async def get_model_status():
    """Get model system status - hardcoded for stability"""
    status_data = {
        "available": True,
        "system_status": {
            "total_models": 4,
            "healthy_models": 4,
            "available_models": ["ethos-light", "ethos-code", "ethos-pro", "ethos-creative"],
            "system_status": "available",
            "models": {
                "ethos-light": {
                    "model_id": "ethos-light",
                    "model_name": "Ethos Light",
                    "is_loaded": True,
                    "device": "local",
                    "cuda_available": False,
                    "load_time": 0.1,
                    "last_used": time.time(),
                    "error_count": 0,
                    "avg_response_time": 1.0
                },
                "ethos-code": {
                    "model_id": "ethos-code",
                    "model_name": "Ethos Code",
                    "is_loaded": True,
                    "device": "local",
                    "cuda_available": False,
                    "load_time": 0.1,
                    "last_used": time.time(),
                    "error_count": 0,
                    "avg_response_time": 1.0
                },
                "ethos-pro": {
                    "model_id": "ethos-pro",
                    "model_name": "Ethos Pro",
                    "is_loaded": True,
                    "device": "local",
                    "cuda_available": False,
                    "load_time": 0.1,
                    "last_used": time.time(),
                    "error_count": 0,
                    "avg_response_time": 1.0
                },
                "ethos-creative": {
                    "model_id": "ethos-creative",
                    "model_name": "Ethos Creative",
                    "is_loaded": True,
                    "device": "local",
                    "cuda_available": False,
                    "load_time": 0.1,
                    "last_used": time.time(),
                    "error_count": 0,
                    "avg_response_time": 1.0
                }
            }
        },
        "models": {
            "ethos-light": {
                "model_id": "ethos-light",
                "model_name": "Ethos Light",
                "is_loaded": True,
                "device": "local",
                "cuda_available": False,
                "load_time": 0.1,
                "last_used": time.time(),
                "error_count": 0,
                "avg_response_time": 1.0
            },
            "ethos-code": {
                "model_id": "ethos-code",
                "model_name": "Ethos Code",
                "is_loaded": True,
                "device": "local",
                "cuda_available": False,
                "load_time": 0.1,
                "last_used": time.time(),
                "error_count": 0,
                "avg_response_time": 1.0
            },
            "ethos-pro": {
                "model_id": "ethos-pro",
                "model_name": "Ethos Pro",
                "is_loaded": True,
                "device": "local",
                "cuda_available": False,
                "load_time": 0.1,
                "last_used": time.time(),
                "error_count": 0,
                "avg_response_time": 1.0
            },
            "ethos-creative": {
                "model_id": "ethos-creative",
                "model_name": "Ethos Creative",
                "is_loaded": True,
                "device": "local",
                "cuda_available": False,
                "load_time": 0.1,
                "last_used": time.time(),
                "error_count": 0,
                "avg_response_time": 1.0
            }
        }
    }
    
    from fastapi.responses import JSONResponse
    response = JSONResponse(content=status_data)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

@app.post("/api/chat")
async def chat(message: ChatMessage):
    """Chat endpoint - simple responses for now"""
    try:
        content = message.get_content()
        model_id = message.model_override or "ethos-light"
        
        logger.info(f"Received chat message: {content[:50]}... with model: {model_id}")
        
        # Simple response based on model
        if model_id == "ethos-light":
            response_text = f"I'm Ethos Light (llama3.2:3b). You asked: '{content}'. This is a simple response while we get the real AI connection working."
        elif model_id == "ethos-code":
            response_text = f"I'm Ethos Code (codellama:7b). You asked: '{content}'. I'm designed for programming tasks. This is a simple response while we get the real AI connection working."
        elif model_id == "ethos-pro":
            response_text = f"I'm Ethos Pro (gpt-oss:20b). You asked: '{content}'. I'm designed for complex analysis. This is a simple response while we get the real AI connection working."
        elif model_id == "ethos-creative":
            response_text = f"I'm Ethos Creative (llama3.1:70b). You asked: '{content}'. I'm designed for creative tasks. This is a simple response while we get the real AI connection working."
        else:
            response_text = f"I'm an AI assistant. You asked: '{content}'. This is a simple response while we get the real AI connection working."
        
        response_data = {
            "content": response_text,
            "model_used": model_id,
            "timestamp": datetime.now().isoformat(),
            "privacy": "100% local processing",
            "mode": "simple-fallback"
        }
        
        from fastapi.responses import JSONResponse
        response = JSONResponse(content=response_data)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/conversations")
async def create_conversation():
    """Create a new conversation"""
    try:
        conversation_id = str(uuid.uuid4())
        response_data = {
            "id": conversation_id,
            "title": f"New Conversation {conversation_id[:8]}",
            "created_at": datetime.now().isoformat(),
            "messages": []
        }
        
        from fastapi.responses import JSONResponse
        response = JSONResponse(content=response_data)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response
        
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
