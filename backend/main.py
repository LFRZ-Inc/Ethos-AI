#!/usr/bin/env python3
"""
Ethos AI - Real AI with Ollama Bridge
Railway will definitely use this file
"""

import os
import time
import uuid
import requests
import logging
from datetime import datetime
from fastapi import FastAPI
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

# Ollama Bridge - Direct implementation
class OllamaBridge:
    def __init__(self):
        # Use the new localtunnel URL that was just generated
        self.ollama_url = "https://breezy-fireant-86.loca.lt"
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
    
    def get_available_models(self) -> list:
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
            if "70b" in ollama_model:
                timeout = 300  # 5 minutes for 70B models
            elif "20b" in ollama_model:
                timeout = 180  # 3 minutes for 20B models
            elif "7b" in ollama_model:
                timeout = 120  # 2 minutes for 7B models
            else:
                timeout = 60   # 1 minute for 3B models
                
            logger.info(f"Requesting response from {ollama_model} with {timeout}s timeout")
            
            response = requests.post(
                f"{self.ollama_url}/api/generate", 
                json=payload, 
                headers=self.headers,
                timeout=timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get("response", "")
                logger.info(f"Successfully got response from {ollama_model}")
                return ai_response
            else:
                logger.error(f"Ollama request failed: {response.status_code}")
                return None
        except requests.exceptions.Timeout:
            logger.error(f"Timeout getting response from {ollama_model}")
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

@app.get("/test")
async def test():
    return {"test": "working", "timestamp": time.time()}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "ethos-ai-backend",
        "mode": "real-ai",
        "ollama_available": OLLAMA_AVAILABLE,
        "timestamp": time.time(),
        "environment": "production"
    }

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
                    "ollama_model": ollama_model,
                    "capabilities": ["real_ai", "privacy_focused", "local_processing"]
                })
            
            return {
                "models": models_data,
                "total": len([m for m in models_data if m["enabled"]]),
                "status": "available" if any(m["enabled"] for m in models_data) else "unavailable",
                "ollama_available": True,
                "ollama_models": available_models
            }
        except Exception as e:
            logger.error(f"Error getting models: {e}")
            return get_fallback_models()
    else:
        return get_fallback_models()

def get_fallback_models():
    """Fallback models when Ollama is not available"""
    return {
        "models": [
            {
                "id": "ethos-light",
                "name": "Ethos Light",
                "type": "local",
                "provider": "ollama",
                "enabled": False,
                "status": "unavailable",
                "ollama_model": "llama3.2:3b",
                "capabilities": ["real_ai", "privacy_focused", "local_processing"]
            },
            {
                "id": "ethos-code",
                "name": "Ethos Code",
                "type": "local",
                "provider": "ollama",
                "enabled": False,
                "status": "unavailable",
                "ollama_model": "codellama:7b",
                "capabilities": ["real_ai", "privacy_focused", "local_processing"]
            },
            {
                "id": "ethos-pro",
                "name": "Ethos Pro",
                "type": "local",
                "provider": "ollama",
                "enabled": False,
                "status": "unavailable",
                "ollama_model": "gpt-oss:20b",
                "capabilities": ["real_ai", "privacy_focused", "local_processing"]
            },
            {
                "id": "ethos-creative",
                "name": "Ethos Creative",
                "type": "local",
                "provider": "ollama",
                "enabled": False,
                "status": "unavailable",
                "ollama_model": "llama3.1:70b",
                "capabilities": ["real_ai", "privacy_focused", "local_processing"]
            }
        ],
        "total": 0,
        "status": "unavailable",
        "ollama_available": False,
        "ollama_models": []
    }

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
            
            return {
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
            return get_fallback_status()
    else:
        return get_fallback_status()

def get_fallback_status():
    """Fallback status when Ollama is not available"""
    return {
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

@app.post("/api/chat")
async def chat(message: ChatMessage):
    """Chat endpoint - Real AI responses"""
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
        
        # Add explicit CORS headers to fix the CORS error
        from fastapi.responses import JSONResponse
        response = JSONResponse(content=response_data)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        error_data = {
            "content": f"Error: {str(e)}",
            "model_used": model_id if 'model_id' in locals() else "unknown",
            "timestamp": datetime.now().isoformat(),
            "privacy": "100% local processing",
            "mode": "error"
        }
        
        # Add explicit CORS headers to error response too
        from fastapi.responses import JSONResponse
        response = JSONResponse(content=error_data)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response

@app.post("/api/conversations")
async def create_conversation():
    """Create a new conversation"""
    conversation_id = str(uuid.uuid4())
    return {
        "id": conversation_id,
        "title": f"New Conversation {conversation_id[:8]}",
        "created_at": datetime.now().isoformat(),
        "messages": []
    }

@app.get("/api/conversations")
async def get_conversations():
    """Get all conversations"""
    return {
        "conversations": [],
        "total": 0
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port) 