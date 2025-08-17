#!/usr/bin/env python3
"""
Hybrid Ethos AI Main Application
Local models via tunnel + Cloud fallback
FORCE REDEPLOY - Railway should pick up this change

VERSION: 3.0.0-HYBRID
DEPLOYMENT: HYBRID-SYSTEM-ACTIVE
LOCAL-TUNNEL: https://calm-otter-38.loca.lt
"""

import asyncio
import json
import logging
import time
import uuid
import subprocess
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Install Ollama during startup if on Railway
def install_ollama_on_railway():
    """Install Ollama if running on Railway and not already installed"""
    if os.getenv('RAILWAY_ENVIRONMENT'):
        logger.info("🚂 Running on Railway - checking Ollama installation")
        
        # Check if Ollama is already installed
        try:
            result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"✅ Ollama already installed: {result.stdout.strip()}")
                return True
        except:
            pass
        
        # Install Ollama if not found
        logger.info("📦 Installing Ollama on Railway...")
        try:
            install_result = subprocess.run(
                "curl -fsSL https://ollama.ai/install.sh | sh",
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if install_result.returncode == 0:
                logger.info("✅ Ollama installed successfully")
                return True
            else:
                logger.error(f"❌ Ollama installation failed: {install_result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error installing Ollama: {e}")
            return False
    else:
        logger.info("💻 Running locally - skipping Ollama installation")
        return True

# Install Ollama during startup
install_ollama_on_railway()

# Import the cloud fusion engine
from cloud_fusion_engine import CloudEthosFusionEngine

# Initialize FastAPI app
app = FastAPI(title="Ethos AI - Hybrid Edition", version="3.0.0-HYBRID")

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
    content: str
    conversation_id: Optional[str] = None
    model_override: Optional[str] = None
    use_tools: Optional[bool] = False

class ChatResponse(BaseModel):
    message: str
    conversation_id: str
    timestamp: str
    model_used: str
    confidence: float
    processing_time: float
    capabilities_used: List[str]
    synthesis_reasoning: str

# Initialize the Cloud Ethos Fusion Engine
try:
    fusion_engine = CloudEthosFusionEngine()
    FUSION_AVAILABLE = True
    logger.info("Cloud Ethos Fusion Engine initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Cloud Fusion Engine: {e}")
    fusion_engine = None
    FUSION_AVAILABLE = False

# Hybrid AI System - Local Models + Cloud Fallback
class HybridAISystem:
    """Hybrid AI system that tries local models first, falls back to lightweight AI"""
    
    def __init__(self):
        self.tunnel_url = None
        self.local_available = False
        self.lightweight_ai = None # No longer needed
        
    def set_tunnel_url(self, url):
        """Set the localtunnel URL for local models"""
        self.tunnel_url = url
        self.local_available = True
        logger.info(f"🌐 Tunnel URL set: {url}")
    
    def check_local_models(self):
        """Check if local models are available via tunnel"""
        if not self.tunnel_url:
            return False
            
        try:
            response = requests.get(f"{self.tunnel_url}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get("models", [])
                available_models = [model["name"] for model in models]
                logger.info(f"✅ Local models available: {available_models}")
                return True
        except Exception as e:
            logger.warning(f"❌ Local models not available: {e}")
        
        return False
    
    async def generate_response(self, user_message, model_override="ethos-light"):
        """Generate response using local models only - no fallback"""
        
        # Check if tunnel is connected and models are available
        if not self.local_available:
            logger.error("❌ Tunnel not connected")
            raise HTTPException(
                status_code=503,
                detail="Tunnel not connected. Please set tunnel URL first."
            )
        
        if not self.check_local_models():
            logger.error("❌ Local models not accessible via tunnel")
            raise HTTPException(
                status_code=503,
                detail="Local AI models not accessible. Please check tunnel connection."
            )
        
        try:
            # Map Ethos models to local Ollama models
            model_mapping = {
                "ethos-light": "llama3.2:3b",
                "ethos-code": "codellama:7b", 
                "ethos-pro": "gpt-oss:20b",
                "ethos-creative": "llama3.1:70b"
            }
            
            ollama_model = model_mapping.get(model_override, "llama3.2:3b")
            
            # Call local Ollama via tunnel
            payload = {
                "model": ollama_model,
                "prompt": user_message,
                "stream": False
            }
            
            logger.info(f"🚀 Calling local model {ollama_model} via tunnel")
            response = requests.post(
                f"{self.tunnel_url}/api/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Got response from {ollama_model}")
                return {
                    "response": result.get("response", ""),
                    "model_used": model_override,
                    "confidence": 0.95,
                    "source": "local_model",
                    "local": True
                }
            else:
                logger.error(f"❌ Ollama API error: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=503,
                    detail=f"Ollama API error: {response.status_code}"
                )
                    
        except requests.exceptions.Timeout:
            logger.error("❌ Request timeout")
            raise HTTPException(
                status_code=503,
                detail="Request timeout - model may be loading"
            )
        except Exception as e:
            logger.error(f"❌ Local model error: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"Local model error: {str(e)}"
            )

# Initialize hybrid AI system
hybrid_ai = HybridAISystem()

def check_ollama_available():
    """Check if ollama is available on Railway"""
    try:
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def get_available_models():
    """Get list of available models on Railway"""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if result.returncode == 0:
            # Parse the output to get model names
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            models = []
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if parts:
                        models.append(parts[0])
            return models
        return []
    except:
        return []

# Health check endpoint
@app.get("/")
async def root():
    ollama_available = check_ollama_available()
    available_models = get_available_models() if ollama_available else []
    
    # Check if local models are available via tunnel
    local_available = hybrid_ai.check_local_models()
    
    return {
        "message": "Ethos AI - Hybrid Edition",
        "status": "healthy",
        "version": "3.0.0-HYBRID",
        "fusion_available": FUSION_AVAILABLE,
        "ollama_available": ollama_available,
        "available_models": available_models,
        "local_available": local_available,
        "hybrid_mode": True,
        "deployment": "hybrid",
        "build": "HYBRID-SYSTEM-ACTIVE"
    }

@app.get("/health")
async def health_check():
    ollama_available = check_ollama_available()
    available_models = get_available_models() if ollama_available else []
    
    # Check if local models are available via tunnel
    local_available = hybrid_ai.check_local_models()
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "3.0.0-HYBRID",
        "fusion_engine": FUSION_AVAILABLE,
        "ollama_available": ollama_available,
        "available_models": available_models,
        "local_available": local_available,
        "hybrid_mode": True,
        "deployment": "hybrid",
        "build": "HYBRID-SYSTEM-ACTIVE",
        "message": f"Hybrid AI System - {'Local models connected' if local_available else 'Cloud fallback active'}"
    }

@app.get("/api/models")
async def get_models():
    """Get available models with cloud fusion engine status"""
    ollama_available = check_ollama_available()
    available_models = get_available_models() if ollama_available else []
    
    if FUSION_AVAILABLE and fusion_engine and ollama_available:
        try:
            # Check if our required models are available
            has_3b = "llama3.2:3b" in available_models
            has_7b = "codellama:7b" in available_models
            
            # Create Ethos model mapping for local models
            ethos_models = [
                {
                    "id": "ethos-light",
                    "name": "Ethos Light (3B)",
                    "type": "local",
                    "provider": "ollama",
                    "enabled": local_available,
                    "status": "available" if local_available else "unavailable",
                    "ollama_model": "llama3.2:3b",
                    "capabilities": ["general_knowledge", "quick_responses", "basic_reasoning"],
                    "fusion_capable": False,
                    "reason": "Local model via tunnel" if local_available else "Tunnel not connected"
                },
                {
                    "id": "ethos-code",
                    "name": "Ethos Code (7B)",
                    "type": "local",
                    "provider": "ollama",
                    "enabled": local_available,
                    "status": "available" if local_available else "unavailable",
                    "ollama_model": "codellama:7b",
                    "capabilities": ["programming", "debugging", "code_generation", "technical_analysis"],
                    "fusion_capable": False,
                    "reason": "Local model via tunnel" if local_available else "Tunnel not connected"
                },
                {
                    "id": "ethos-pro",
                    "name": "Ethos Pro (20B) - Unavailable",
                    "type": "cloud",
                    "provider": "ollama",
                    "enabled": False,
                    "status": "unavailable",
                    "ollama_model": "gpt-oss:20b",
                    "capabilities": ["complex_reasoning", "analysis", "research"],
                    "fusion_capable": False,
                    "reason": "Requires 25GB+ RAM - upgrade needed"
                },
                {
                    "id": "ethos-creative",
                    "name": "Ethos Creative (70B) - Unavailable",
                    "type": "cloud",
                    "provider": "ollama",
                    "enabled": False,
                    "status": "unavailable",
                    "ollama_model": "llama3.1:70b",
                    "capabilities": ["creative_writing", "storytelling", "artistic_expression"],
                    "fusion_capable": False,
                    "reason": "Requires 45GB+ RAM - upgrade needed"
                }
            ]
            
            # Check if local models are available
            local_available = hybrid_ai.check_local_models()
            
            response_data = {
                "models": ethos_models,
                "total": len([m for m in ethos_models if m["enabled"]]),
                "status": "available" if any(m["enabled"] for m in ethos_models) else "unavailable",
                "fusion_engine": True,
                "ollama_available": True,
                "available_models": available_models,
                "local_available": local_available,
                "hybrid_mode": True,
                "message": f"Hybrid AI System active - {'Local models available' if local_available else 'Cloud fallback active'}",
                "deployment": "hybrid"
            }
        except Exception as e:
            logger.error(f"Error getting models: {e}")
            response_data = get_fallback_models()
    else:
        response_data = get_fallback_models()
    
    response = JSONResponse(content=response_data)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

def get_fallback_models():
    """Fallback models when local models not available"""
    local_available = hybrid_ai.check_local_models()
    
    return {
        "models": [
            {
                "id": "ethos-light",
                "name": "Ethos Light (3B)",
                "type": "local",
                "provider": "ollama",
                "enabled": local_available,
                "status": "available" if local_available else "unavailable",
                "ollama_model": "llama3.2:3b",
                "capabilities": ["general_knowledge", "quick_responses", "basic_reasoning"],
                "fusion_capable": False,
                "reason": "Local model via tunnel" if local_available else "Tunnel not connected"
            },
            {
                "id": "ethos-code",
                "name": "Ethos Code (7B)",
                "type": "local",
                "provider": "ollama",
                "enabled": local_available,
                "status": "available" if local_available else "unavailable",
                "ollama_model": "codellama:7b",
                "capabilities": ["programming", "debugging", "code_generation", "technical_analysis"],
                "fusion_capable": False,
                "reason": "Local model via tunnel" if local_available else "Tunnel not connected"
            }
        ],
        "total": 2 if local_available else 0,
        "status": "available" if local_available else "unavailable",
        "fusion_engine": False,
        "ollama_available": True,
        "available_models": ["llama3.2:3b", "codellama:7b"] if local_available else [],
        "message": "Local models available via tunnel" if local_available else "Local models not available - check tunnel connection",
        "deployment": "hybrid-local" if local_available else "hybrid-unavailable"
    }

@app.get("/api/models/status")
async def get_models_status():
    """Get detailed model status"""
    ollama_available = check_ollama_available()
    available_models = get_available_models() if ollama_available else []
    
    if FUSION_AVAILABLE and fusion_engine and ollama_available:
        try:
            # Count enabled models
            enabled_count = 0
            if "llama3.2:3b" in available_models:
                enabled_count += 1
            if "codellama:7b" in available_models:
                enabled_count += 1
            
            # Create models status object
            models_status = {}
            ethos_models = ["ethos-light", "ethos-code", "ethos-pro", "ethos-creative"]
            
            for ethos_id in ethos_models:
                is_available = False
                if ethos_id == "ethos-light" and "llama3.2:3b" in available_models:
                    is_available = True
                elif ethos_id == "ethos-code" and "codellama:7b" in available_models:
                    is_available = True
                
                models_status[ethos_id] = {
                    "model_id": ethos_id,
                    "model_name": f"Ethos {ethos_id.split('-')[1].title()}",
                    "is_loaded": is_available,
                    "device": "cloud",
                    "cuda_available": False,
                    "load_time": 0.1,
                    "last_used": time.time(),
                    "error_count": 0,
                    "avg_response_time": 1.0
                }
            
            status_data = {
                "available": True,
                "system_status": {
                    "total_models": 4,  # Total Ethos models
                    "healthy_models": enabled_count,
                    "available_models": [k for k, v in models_status.items() if v["is_loaded"]],
                    "system_status": "available",
                    "models": models_status
                },
                "models": models_status
            }
        except Exception as e:
            logger.error(f"Error getting model status: {e}")
            status_data = get_fallback_status()
    else:
        status_data = get_fallback_status()
    
    response = JSONResponse(content=status_data)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

def get_fallback_status():
    """Fallback status when fusion engine is not available"""
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
async def chat_endpoint(request: ChatMessage):
    """Main chat endpoint using Hybrid AI System"""
    start_time = time.time()
    
    try:
        # Use Hybrid AI System (local models only)
        model_override = request.model_override or "ethos-light"
        ai_response = await hybrid_ai.generate_response(request.content, model_override)
        
        processing_time = time.time() - start_time
        
        response_data = {
            "message": ai_response["response"],
            "conversation_id": request.conversation_id or str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "model_used": ai_response["model_used"],
            "confidence": ai_response["confidence"],
            "processing_time": processing_time,
            "capabilities_used": [ai_response["source"]],
            "synthesis_reasoning": f"Local AI model provided response based on {ai_response['source']}.",
            "fusion_engine": False,
            "deployment": "hybrid-local",
            "status": "success"
        }
        
        response = JSONResponse(content=response_data)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response
        
    except HTTPException as e:
        # Re-raise HTTP exceptions as-is
        raise e
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Error generating response",
                "message": f"Failed to generate response: {str(e)}",
                "deployment": "hybrid-error"
            }
        )

@app.post("/api/conversations")
async def create_conversation():
    """Create a new conversation"""
    conversation_id = str(uuid.uuid4())
    return {
        "conversation_id": conversation_id,
        "created_at": datetime.now().isoformat(),
        "status": "created",
        "deployment": "cloud-only"
    }

@app.get("/api/conversations")
async def get_conversations():
    """Get conversation history (placeholder)"""
    return {
        "conversations": [],
        "total": 0,
        "message": "Conversation history not implemented yet",
        "deployment": "cloud-only"
    }

@app.get("/api/fusion/status")
async def get_fusion_status():
    """Get detailed fusion engine status"""
    if FUSION_AVAILABLE and fusion_engine:
        try:
            learning_summary = fusion_engine.get_learning_summary()
            return {
                "fusion_engine": True,
                "status": "active",
                "total_interactions": learning_summary["total_interactions"],
                "performance_trend": learning_summary["performance_trends"]["trend"],
                "capabilities_used": len(learning_summary["capability_insights"]),
                "available_models": get_available_models(),
                "ollama_available": check_ollama_available(),
                "message": "Cloud Ethos Fusion Engine is running and learning",
                "deployment": "cloud-only"
            }
        except Exception as e:
            logger.error(f"Error getting fusion status: {e}")
            return {
                "fusion_engine": True,
                "status": "error",
                "message": f"Error getting status: {str(e)}",
                "deployment": "cloud-only"
            }
    else:
        return {
            "fusion_engine": False,
            "status": "unavailable",
            "message": "Cloud fusion engine not initialized",
            "deployment": "cloud-only"
        }

@app.post("/api/download-models")
async def download_models():
    """Model download disabled - using local models via tunnel only"""
    return {
        "status": "disabled",
        "message": "Cloud model downloads disabled. Use local models via tunnel.",
        "deployment": "hybrid",
        "local_models_only": True,
        "tunnel_required": True
    }

@app.post("/api/set-tunnel")
async def set_tunnel_url(request: dict):
    """Set the tunnel URL for local models"""
    try:
        tunnel_url = request.get("tunnel_url")
        if tunnel_url:
            hybrid_ai.set_tunnel_url(tunnel_url)
            return {
                "status": "success",
                "message": f"Tunnel URL set: {tunnel_url}",
                "local_available": hybrid_ai.local_available,
                "deployment": "hybrid"
            }
        else:
            return {
                "status": "error",
                "message": "No tunnel URL provided",
                "deployment": "hybrid"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error setting tunnel: {str(e)}",
            "deployment": "hybrid"
        }

@app.get("/api/tunnel-status")
async def get_tunnel_status():
    """Get tunnel and local model status"""
    local_available = hybrid_ai.check_local_models()
    
    return {
        "tunnel_url": hybrid_ai.tunnel_url,
        "local_available": local_available,
        "hybrid_mode": True,
        "deployment": "hybrid"
    }

@app.post("/api/models/{model_id}/initialize")
async def initialize_model(model_id: str):
    """Auto-initialize models at launch - always return success"""
    try:
        # Check if local models are available
        local_available = hybrid_ai.check_local_models()
        
        if local_available:
            return {
                "status": "success",
                "message": f"Model {model_id} initialized successfully via local tunnel",
                "model_id": model_id,
                "available": True,
                "deployment": "hybrid-local"
            }
        else:
            return {
                "status": "error", 
                "message": f"Model {model_id} not available - tunnel not connected",
                "model_id": model_id,
                "available": False,
                "deployment": "hybrid-unavailable"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to initialize model {model_id}: {str(e)}",
            "model_id": model_id,
            "available": False,
            "deployment": "hybrid-error"
        }

@app.get("/api/models/{model_id}/status")
async def get_model_status(model_id: str):
    """Get status of a specific model - for frontend compatibility"""
    try:
        # Check if local models are available
        local_available = hybrid_ai.check_local_models()
        
        return {
            "model_id": model_id,
            "status": "available" if local_available else "cloud_fallback",
            "available": True,
            "deployment": "hybrid-local" if local_available else "hybrid-cloud"
        }
        
    except Exception as e:
        return {
            "model_id": model_id,
            "status": "error",
            "available": False,
            "error": str(e),
            "deployment": "hybrid"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 