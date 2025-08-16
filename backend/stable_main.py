#!/usr/bin/env python3
"""
Ethos AI - Stable Backend with Ollama Connection
Designed to work reliably on Railway without crashing
"""

import os
import time
import logging
import uuid
import requests
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
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

# Ollama Bridge - Direct implementation without heavy imports
class OllamaBridge:
    def __init__(self):
        # Use localtunnel URL for cloud access
        self.ollama_url = "https://ethos-ollama.loca.lt"
        self.model_mapping = {
            "ethos-light": "llama3.2:3b",
            "ethos-code": "codellama:7b", 
            "ethos-pro": "gpt-oss:20b",
            "ethos-creative": "llama3.1:70b"
        }
        self.headers = {"User-Agent": "Ethos-AI-Cloud/1.0"}
    
    def is_available(self) -> bool:
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", headers=self.headers, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_available_models(self) -> List[str]:
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", headers=self.headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
            return []
        except:
            return []
    
    def generate_response(self, message: str, model_id: str = "ethos-light") -> Optional[str]:
        try:
            ollama_model = self.model_mapping.get(model_id.lower(), "llama3.2:3b")
            available_models = self.get_available_models()
            
            if ollama_model not in available_models:
                logger.warning(f"Model {ollama_model} not available. Available: {available_models}")
                return None
            
            payload = {
                "model": ollama_model,
                "prompt": message,
                "stream": False
            }
            
            # Use longer timeout for larger models
            if "20b" in ollama_model or "70b" in ollama_model:
                timeout = 180
            elif "7b" in ollama_model:
                timeout = 120
            else:
                timeout = 60
                
            response = requests.post(
                f"{self.ollama_url}/api/generate", 
                json=payload, 
                headers=self.headers,
                timeout=timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                logger.error(f"Ollama request failed: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return None

# Initialize Ollama bridge
try:
    ollama_bridge = OllamaBridge()
    OLLAMA_AVAILABLE = ollama_bridge.is_available()
    logger.info(f"Ollama bridge initialized. Available: {OLLAMA_AVAILABLE}")
except Exception as e:
    logger.error(f"Failed to initialize Ollama bridge: {e}")
    ollama_bridge = None
    OLLAMA_AVAILABLE = False

@app.get("/")
async def root():
    return {"message": "Ethos AI Backend is running!", "status": "healthy"}

@app.get("/health")
async def health_check():
    health_data = {
        "status": "healthy",
        "service": "ethos-ai-backend",
        "mode": "ollama-bridge",
        "ollama_available": OLLAMA_AVAILABLE,
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
    if OLLAMA_AVAILABLE and ollama_bridge:
        try:
            available_models = ollama_bridge.get_available_models()
            models_data = []
            
            for ethos_id, ollama_model in ollama_bridge.model_mapping.items():
                is_available = ollama_model in available_models
                models_data.append({
                    "id": ethos_id,
                    "name": f"Ethos {ethos_id.split('-')[1].title()}",
                    "type": "local",
                    "provider": "ollama",
                    "enabled": is_available,
                    "status": "available" if is_available else "unavailable",
                    "ollama_model": ollama_model
                })
            
            response_data = {
                "models": models_data,
                "total": len([m for m in models_data if m["enabled"]]),
                "status": "available" if any(m["enabled"] for m in models_data) else "unavailable",
                "ollama_available": True,
                "ollama_models": available_models
            }
        except Exception as e:
            logger.error(f"Error getting models: {e}")
            response_data = {
                "models": [],
                "total": 0,
                "status": "unavailable",
                "ollama_available": False,
                "ollama_models": []
            }
    else:
        response_data = {
            "models": [],
            "total": 0,
            "status": "unavailable",
            "ollama_available": False,
            "ollama_models": []
        }
    
    from fastapi.responses import JSONResponse
    response = JSONResponse(content=response_data)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

@app.get("/api/models/status")
async def get_model_status():
    if OLLAMA_AVAILABLE and ollama_bridge:
        try:
            available_models = ollama_bridge.get_available_models()
            models_status = {}
            
            for ethos_id, ollama_model in ollama_bridge.model_mapping.items():
                is_available = ollama_model in available_models
                models_status[ethos_id] = {
                    "model_id": ethos_id,
                    "model_name": f"Ethos {ethos_id.split('-')[1].title()}",
                    "is_loaded": is_available,
                    "device": "local",
                    "cuda_available": False,
                    "load_time": 0.1,
                    "last_used": time.time(),
                    "error_count": 0,
                    "avg_response_time": 1.0
                }
            
            status_data = {
                "available": True,
                "system_status": {
                    "total_models": len(models_status),
                    "healthy_models": len([m for m in models_status.values() if m["is_loaded"]]),
                    "available_models": [k for k, v in models_status.items() if v["is_loaded"]],
                    "system_status": "available",
                    "models": models_status
                },
                "models": models_status
            }
        except Exception as e:
            logger.error(f"Error getting model status: {e}")
            status_data = {
                "available": False,
                "system_status": {
                    "total_models": 0,
                    "healthy_models": 0,
                    "available_models": [],
                    "system_status": "unavailable",
                    "models": {}
                },
                "models": {}
            }
    else:
        status_data = {
            "available": False,
            "system_status": {
                "total_models": 0,
                "healthy_models": 0,
                "available_models": [],
                "system_status": "unavailable",
                "models": {}
            },
            "models": {}
        }
    
    from fastapi.responses import JSONResponse
    response = JSONResponse(content=status_data)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

@app.post("/api/chat")
async def chat(message: ChatMessage):
    try:
        content = message.get_content()
        model_id = message.model_override or "ethos-light"
        
        logger.info(f"Received chat message: {content[:50]}... with model: {model_id}")
        
        if OLLAMA_AVAILABLE and ollama_bridge:
            # Try to get real AI response
            ai_response = ollama_bridge.generate_response(content, model_id)
            
            if ai_response:
                response_data = {
                    "content": ai_response,
                    "model_used": model_id,
                    "timestamp": datetime.now().isoformat(),
                    "privacy": "100% local processing",
                    "mode": "real-ai"
                }
            else:
                response_data = {
                    "content": "Error: Could not get response from Ollama. Please check your local setup and tunnel connection.",
                    "model_used": model_id,
                    "timestamp": datetime.now().isoformat(),
                    "privacy": "100% local processing",
                    "mode": "error"
                }
        else:
            response_data = {
                "content": "Error: Ollama is not available. Please check your local Ollama setup and tunnel connection.",
                "model_used": model_id,
                "timestamp": datetime.now().isoformat(),
                "privacy": "100% local processing",
                "mode": "error"
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
