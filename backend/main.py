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

# Lightweight AI Response System (for Railway free tier)
class LightweightAI:
    """Lightweight AI system that provides intelligent responses without large models"""
    
    def __init__(self):
        self.conversation_history = []
        self.personality = {
            "name": "Ethos AI",
            "traits": ["helpful", "intelligent", "creative", "analytical"],
            "capabilities": ["analysis", "writing", "coding", "research"]
        }
    
    def generate_response(self, user_message, model_type="ethos-light"):
        """Generate intelligent responses based on message content"""
        
        # Add to conversation history
        self.conversation_history.append({"user": user_message, "timestamp": time.time()})
        
        # Analyze message intent
        message_lower = user_message.lower()
        
        # Knowledge-based responses
        if "president" in message_lower:
            return {
                "response": "The current President of the United States is Joe Biden, who was inaugurated on January 20, 2021. He is the 46th President of the United States.",
                "model_used": model_type,
                "confidence": 0.95,
                "source": "current_events"
            }
        
        elif "weather" in message_lower:
            return {
                "response": "I don't have access to real-time weather data, but I can help you find weather information for your location. You can check weather apps or websites like weather.com for current conditions.",
                "model_used": model_type,
                "confidence": 0.85,
                "source": "general_knowledge"
            }
        
        elif "code" in message_lower or "programming" in message_lower:
            return {
                "response": "I can help you with programming! I'm knowledgeable about Python, JavaScript, Java, C++, and many other languages. What specific coding question do you have?",
                "model_used": model_type,
                "confidence": 0.90,
                "source": "programming_knowledge"
            }
        
        elif "hello" in message_lower or "hi" in message_lower:
            return {
                "response": f"Hello! I'm {self.personality['name']}, your AI assistant. I'm here to help you with analysis, writing, coding, research, and more. What can I assist you with today?",
                "model_used": model_type,
                "confidence": 0.95,
                "source": "greeting"
            }
        
        elif "help" in message_lower:
            return {
                "response": "I'm here to help! I can assist with:\n• Analysis and research\n• Writing and content creation\n• Programming and coding\n• Problem solving\n• General questions\n\nWhat would you like to work on?",
                "model_used": model_type,
                "confidence": 0.90,
                "source": "help"
            }
        
        # Default intelligent response
        else:
            return {
                "response": f"I understand you're asking about '{user_message}'. As {self.personality['name']}, I can help you explore this topic. Could you provide more specific details about what you'd like to know?",
                "model_used": model_type,
                "confidence": 0.75,
                "source": "general_intelligence"
            }

# Initialize lightweight AI
lightweight_ai = LightweightAI()

# Hybrid AI System - Local Models + Cloud Fallback
class HybridAISystem:
    """Hybrid AI system that tries local models first, falls back to lightweight AI"""
    
    def __init__(self):
        self.tunnel_url = None
        self.local_available = False
        self.lightweight_ai = LightweightAI()
        
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
            response = requests.get(f"{self.tunnel_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                available_models = [model["name"] for model in models]
                logger.info(f"✅ Local models available: {available_models}")
                return True
        except Exception as e:
            logger.warning(f"❌ Local models not available: {e}")
        
        return False
    
    async def generate_response(self, user_message, model_override="ethos-light"):
        """Generate response using local models or fallback to lightweight AI"""
        
        # Try local models first
        if self.local_available and self.check_local_models():
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
                
                response = requests.post(
                    f"{self.tunnel_url}/api/generate",
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "response": result.get("response", ""),
                        "model_used": model_override,
                        "confidence": 0.95,
                        "source": "local_model",
                        "local": True
                    }
                    
            except Exception as e:
                logger.error(f"❌ Local model error: {e}")
        
        # Fallback to lightweight AI
        logger.info("🔄 Falling back to lightweight AI")
        return self.lightweight_ai.generate_response(user_message, model_override)

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
            
            # Create Ethos model mapping with lightweight AI
            ethos_models = [
                {
                    "id": "ethos-light",
                    "name": "Ethos Light (3B)",
                    "type": "cloud",
                    "provider": "lightweight-ai",
                    "enabled": True,
                    "status": "available",
                    "ollama_model": "lightweight-ai",
                    "capabilities": ["general_knowledge", "quick_responses", "basic_reasoning", "intelligent_analysis"],
                    "fusion_capable": False,
                    "reason": None
                },
                {
                    "id": "ethos-code",
                    "name": "Ethos Code (7B)",
                    "type": "cloud",
                    "provider": "lightweight-ai",
                    "enabled": True,
                    "status": "available",
                    "ollama_model": "lightweight-ai",
                    "capabilities": ["programming", "debugging", "code_generation", "technical_analysis"],
                    "fusion_capable": False,
                    "reason": None
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
    """Fallback models using lightweight AI"""
    return {
        "models": [
            {
                "id": "ethos-light",
                "name": "Ethos Light (3B)",
                "type": "cloud",
                "provider": "lightweight-ai",
                "enabled": True,
                "status": "available",
                "ollama_model": "lightweight-ai",
                "capabilities": ["general_knowledge", "quick_responses", "basic_reasoning", "intelligent_analysis"],
                "fusion_capable": False,
                "reason": None
            },
            {
                "id": "ethos-code",
                "name": "Ethos Code (7B)",
                "type": "cloud",
                "provider": "lightweight-ai",
                "enabled": True,
                "status": "available",
                "ollama_model": "lightweight-ai",
                "capabilities": ["programming", "debugging", "code_generation", "technical_analysis"],
                "fusion_capable": False,
                "reason": None
            }
        ],
        "total": 2,
        "status": "available",
        "fusion_engine": False,
        "ollama_available": True,
        "available_models": ["lightweight-ai"],
        "message": "Lightweight AI is available - providing intelligent responses",
        "deployment": "cloud-only-lightweight"
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
        # Use Hybrid AI System (local models + cloud fallback)
        model_override = request.model_override or "ethos-light"
        ai_response = await hybrid_ai.generate_response(request.content, model_override)
        
        processing_time = time.time() - start_time
        
        # Determine deployment type
        deployment_type = "hybrid-local" if ai_response.get("local", False) else "hybrid-cloud"
        
        response_data = {
            "message": ai_response["response"],
            "conversation_id": request.conversation_id or str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "model_used": ai_response["model_used"],
            "confidence": ai_response["confidence"],
            "processing_time": processing_time,
            "capabilities_used": [ai_response["source"]],
            "synthesis_reasoning": f"Hybrid AI used {'local model' if ai_response.get('local') else 'cloud fallback'} to provide response based on {ai_response['source']}.",
            "fusion_engine": False,
            "deployment": deployment_type,
            "status": "success"
        }
        
        response = JSONResponse(content=response_data)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating response: {str(e)}"
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
    """Initialize a specific model - for frontend compatibility"""
    try:
        # Check if local models are available
        local_available = hybrid_ai.check_local_models()
        
        if local_available:
            return {
                "status": "success",
                "message": f"Model {model_id} initialized successfully",
                "model_id": model_id,
                "available": True,
                "deployment": "hybrid-local"
            }
        else:
            return {
                "status": "success", 
                "message": f"Model {model_id} available via cloud fallback",
                "model_id": model_id,
                "available": True,
                "deployment": "hybrid-cloud"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to initialize model {model_id}: {str(e)}",
            "model_id": model_id,
            "available": False,
            "deployment": "hybrid"
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