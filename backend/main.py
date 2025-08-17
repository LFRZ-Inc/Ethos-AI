#!/usr/bin/env python3
"""
Cloud-Only Ethos AI Main Application
Fully cloud-based - models run directly on Railway!
VERSION: 4.0.0-CLOUD-ONLY
DEPLOYMENT: CLOUD-MODELS-ACTIVE
OLLAMA-INSTALLATION: READY
MODELS: 3B + 7B direct download
"""

import os
import time
import json
import subprocess
import requests
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Ethos AI - Cloud Edition", version="4.0.0-CLOUD-ONLY")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
MODELS_DOWNLOADED = False
DOWNLOAD_IN_PROGRESS = False
OLLAMA_AVAILABLE = False

# Install Ollama during startup
def install_ollama_on_railway():
    """Install Ollama if running on Railway and not already installed"""
    global OLLAMA_AVAILABLE
    if os.getenv('RAILWAY_ENVIRONMENT'):
        logger.info("🚂 Running on Railway - checking Ollama installation")
        try:
            result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"✅ Ollama already installed: {result.stdout.strip()}")
                OLLAMA_AVAILABLE = True
                
                # Start Ollama service in background
                logger.info("🚀 Starting Ollama service...")
                try:
                    subprocess.Popen(['ollama', 'serve'], 
                                   stdout=subprocess.DEVNULL, 
                                   stderr=subprocess.DEVNULL)
                    logger.info("✅ Ollama service started in background")
                    # Wait a moment for service to start
                    import time
                    time.sleep(5)
                except Exception as e:
                    logger.error(f"❌ Failed to start Ollama service: {e}")
                
                return True
        except:
            pass
        logger.info("📦 Installing Ollama on Railway...")
        try:
            install_result = subprocess.run(
                "curl -fsSL https://ollama.ai/install.sh | sh",
                shell=True,
                capture_output=True,
                text=True,
                timeout=300
            )
            if install_result.returncode == 0:
                logger.info("✅ Ollama installed successfully")
                OLLAMA_AVAILABLE = True
                
                # Start Ollama service in background
                logger.info("🚀 Starting Ollama service...")
                try:
                    subprocess.Popen(['ollama', 'serve'], 
                                   stdout=subprocess.DEVNULL, 
                                   stderr=subprocess.DEVNULL)
                    logger.info("✅ Ollama service started in background")
                    # Wait a moment for service to start
                    import time
                    time.sleep(5)
                except Exception as e:
                    logger.error(f"❌ Failed to start Ollama service: {e}")
                
                return True
            else:
                logger.error(f"❌ Ollama installation failed: {install_result.stderr}")
                return False
        except Exception as e:
            logger.error(f"❌ Error installing Ollama: {e}")
            return False
    else:
        logger.info("💻 Running locally - skipping Ollama installation")
        OLLAMA_AVAILABLE = True
        return True

# Download models to Railway
def download_models_to_railway():
    """Download 3B and 7B models directly to Railway"""
    global MODELS_DOWNLOADED, DOWNLOAD_IN_PROGRESS
    
    if MODELS_DOWNLOADED or DOWNLOAD_IN_PROGRESS:
        return MODELS_DOWNLOADED
    
    DOWNLOAD_IN_PROGRESS = True
    logger.info("🚀 Starting model downloads to Railway...")
    
    models_to_download = [
        "llama3.2:3b",
        "codellama:7b"
    ]
    
    try:
        for model in models_to_download:
            logger.info(f"📥 Downloading {model}...")
            result = subprocess.run(
                ['ollama', 'pull', model],
                capture_output=True,
                text=True,
                timeout=1800  # 30 minutes per model
            )
            
            if result.returncode == 0:
                logger.info(f"✅ {model} downloaded successfully")
            else:
                logger.error(f"❌ Failed to download {model}: {result.stderr}")
                DOWNLOAD_IN_PROGRESS = False
                return False
        
        MODELS_DOWNLOADED = True
        DOWNLOAD_IN_PROGRESS = False
        logger.info("🎉 All models downloaded successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error downloading models: {e}")
        DOWNLOAD_IN_PROGRESS = False
        return False

# Check available models
def get_available_models():
    """Get list of available models from Ollama"""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            models = []
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        models.append(parts[0])
            return models
    except Exception as e:
        logger.error(f"Error getting models: {e}")
    return []

# Cloud AI System
class CloudAISystem:
    """Cloud AI system that runs models directly on Railway"""
    
    def __init__(self):
        self.models_ready = False
        self.available_models = []
        self.downloading = False
        
    def initialize_models(self):
        """Initialize models on Railway"""
        global MODELS_DOWNLOADED
        
        if not OLLAMA_AVAILABLE:
            logger.error("❌ Ollama not available")
            return False
            
        if self.downloading:
            logger.info("📥 Models are currently being downloaded...")
            return False
            
        if not MODELS_DOWNLOADED:
            logger.info("📥 Models not downloaded yet, starting download...")
            self.downloading = True
            if download_models_to_railway():
                self.models_ready = True
                self.available_models = get_available_models()
                self.downloading = False
                return True
            else:
                self.downloading = False
                return False
        else:
            self.models_ready = True
            self.available_models = get_available_models()
            return True
    
    async def generate_response(self, user_message, model_override="ethos-light"):
        """Generate response using cloud models"""
        
        if not self.models_ready:
            if not self.initialize_models():
                raise HTTPException(
                    status_code=503,
                    detail="Models not ready. Please wait for download to complete."
                )
        
        try:
            # Map Ethos models to local Ollama models
            model_mapping = {
                "ethos-light": "llama3.2:3b",
                "ethos-code": "codellama:7b"
            }
            
            ollama_model = model_mapping.get(model_override, "llama3.2:3b")
            
            # Check if model is available
            available_models = get_available_models()
            if ollama_model not in available_models:
                # Try to download the specific model
                logger.info(f"📥 Model {ollama_model} not found, downloading...")
                result = subprocess.run(
                    ['ollama', 'pull', ollama_model],
                    capture_output=True,
                    text=True,
                    timeout=1800  # 30 minutes
                )
                
                if result.returncode != 0:
                    raise HTTPException(
                        status_code=503,
                        detail=f"Failed to download model {ollama_model}: {result.stderr}"
                    )
                
                logger.info(f"✅ {ollama_model} downloaded successfully")
            
            logger.info(f"🚀 Calling cloud model {ollama_model}")
            
            # Use subprocess to call Ollama directly
            result = subprocess.run(
                ['ollama', 'run', ollama_model, user_message],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout for cloud models
            )
            
            if result.returncode == 0:
                response_text = result.stdout.strip()
                logger.info(f"✅ Got response from {ollama_model}")
                return {
                    "message": response_text,
                    "model_used": model_override,
                    "confidence": 0.95,
                    "source": "cloud_model",
                    "cloud": True
                }
            else:
                logger.error(f"❌ Ollama error: {result.stderr}")
                raise HTTPException(
                    status_code=503,
                    detail=f"Model error: {result.stderr}"
                )
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Request timeout")
            raise HTTPException(
                status_code=503,
                detail="Request timeout - model may be loading"
            )
        except Exception as e:
            logger.error(f"❌ Cloud model error: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"Cloud model error: {str(e)}"
            )

# Initialize cloud AI system
cloud_ai = CloudAISystem()

# Install Ollama on startup
install_ollama_on_railway()

# API Endpoints
@app.get("/")
async def root():
    available_models = get_available_models() if OLLAMA_AVAILABLE else []
    return {
        "message": "Ethos AI - Cloud Edition",
        "status": "healthy",
        "version": "4.0.0-CLOUD-ONLY",
        "ollama_available": OLLAMA_AVAILABLE,
        "models_downloaded": MODELS_DOWNLOADED,
        "download_in_progress": DOWNLOAD_IN_PROGRESS,
        "available_models": available_models,
        "deployment": "cloud-only",
        "build": "CLOUD-MODELS-ACTIVE"
    }

@app.get("/health")
async def health_check():
    available_models = get_available_models() if OLLAMA_AVAILABLE else []
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "4.0.0-CLOUD-ONLY",
        "ollama_available": OLLAMA_AVAILABLE,
        "models_downloaded": MODELS_DOWNLOADED,
        "download_in_progress": DOWNLOAD_IN_PROGRESS,
        "available_models": available_models,
        "deployment": "cloud-only",
        "build": "CLOUD-MODELS-ACTIVE"
    }

@app.get("/api/models")
async def get_models():
    """Get available models"""
    try:
        if OLLAMA_AVAILABLE:
            available_models = get_available_models()
            has_3b = "llama3.2:3b" in available_models
            has_7b = "codellama:7b" in available_models
            
            # Create Ethos model mapping
            ethos_models = [
                {
                    "id": "ethos-light",
                    "name": "Ethos Light (3B)",
                    "type": "cloud",
                    "provider": "ollama",
                    "enabled": has_3b,
                    "status": "available" if has_3b else "downloading",
                    "ollama_model": "llama3.2:3b",
                    "capabilities": ["general_knowledge", "quick_responses", "basic_reasoning"],
                    "fusion_capable": False,
                    "reason": "Cloud model on Railway" if has_3b else "Downloading to Railway"
                },
                {
                    "id": "ethos-code",
                    "name": "Ethos Code (7B)",
                    "type": "cloud",
                    "provider": "ollama",
                    "enabled": has_7b,
                    "status": "available" if has_7b else "downloading",
                    "ollama_model": "codellama:7b",
                    "capabilities": ["programming", "debugging", "code_generation", "technical_analysis"],
                    "fusion_capable": False,
                    "reason": "Cloud model on Railway" if has_7b else "Downloading to Railway"
                }
            ]
            
            response_data = {
                "models": ethos_models,
                "total": len([m for m in ethos_models if m["enabled"]]),
                "status": "available" if any(m["enabled"] for m in ethos_models) else "downloading",
                "fusion_engine": False,
                "ollama_available": True,
                "available_models": [m["ollama_model"] for m in ethos_models if m["enabled"]],
                "models_downloaded": MODELS_DOWNLOADED,
                "download_in_progress": DOWNLOAD_IN_PROGRESS,
                "message": "Cloud Ethos AI - Models running directly on Railway",
                "deployment": "cloud-only"
            }
        else:
            response_data = get_fallback_models()
            
    except Exception as e:
        logger.error(f"Error getting models: {e}")
        response_data = get_fallback_models()
    
    response = JSONResponse(content=response_data)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

def get_fallback_models():
    """Fallback models when Ollama not available"""
    return {
        "models": [
            {
                "id": "ethos-light",
                "name": "Ethos Light (3B)",
                "type": "cloud",
                "provider": "ollama",
                "enabled": False,
                "status": "unavailable",
                "ollama_model": "llama3.2:3b",
                "capabilities": ["general_knowledge", "quick_responses", "basic_reasoning"],
                "fusion_capable": False,
                "reason": "Ollama not available"
            },
            {
                "id": "ethos-code",
                "name": "Ethos Code (7B)",
                "type": "cloud",
                "provider": "ollama",
                "enabled": False,
                "status": "unavailable",
                "ollama_model": "codellama:7b",
                "capabilities": ["programming", "debugging", "code_generation", "technical_analysis"],
                "fusion_capable": False,
                "reason": "Ollama not available"
            }
        ],
        "total": 0,
        "status": "unavailable",
        "fusion_engine": False,
        "ollama_available": False,
        "available_models": [],
        "message": "Ollama not available",
        "deployment": "cloud-only"
    }

@app.post("/api/chat")
async def chat_endpoint(request: Request):
    """Chat endpoint"""
    try:
        data = await request.json()
        user_message = data.get("content", "")
        model_override = data.get("model_override", "ethos-light")
        
        if not user_message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Generate response using cloud AI
        response_data = await cloud_ai.generate_response(user_message, model_override)
        
        # Add conversation tracking
        response_data.update({
            "conversation_id": data.get("conversation_id", f"conv_{int(time.time())}"),
            "timestamp": datetime.now().isoformat(),
            "processing_time": 0.0,
            "capabilities_used": ["cloud_model"],
            "synthesis_reasoning": "Cloud AI model provided response based on cloud_model.",
            "fusion_engine": False,
            "deployment": "cloud-only",
            "status": "success"
        })
        
        response = JSONResponse(content=response_data)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Error generating response",
                "message": f"Failed to generate response: {str(e)}",
                "deployment": "cloud-only-error"
            }
        )

@app.post("/api/download-models")
async def download_models():
    """Download models to Railway"""
    global MODELS_DOWNLOADED, DOWNLOAD_IN_PROGRESS
    
    if DOWNLOAD_IN_PROGRESS:
        return {
            "status": "in_progress",
            "message": "Models are currently being downloaded",
            "deployment": "cloud-only"
        }
    
    if MODELS_DOWNLOADED:
        return {
            "status": "already_downloaded",
            "message": "Models are already downloaded",
            "deployment": "cloud-only"
        }
    
    # Start download in background
    success = download_models_to_railway()
    
    return {
        "status": "started" if success else "failed",
        "message": "Model download started" if success else "Failed to start download",
        "deployment": "cloud-only"
    }

@app.get("/api/models/status")
async def get_models_status():
    """Get models status"""
    available_models = get_available_models() if OLLAMA_AVAILABLE else []
    
    return {
        "available": OLLAMA_AVAILABLE,
        "system_status": {
            "total_models": 2,
            "healthy_models": len(available_models),
            "available_models": available_models,
            "system_status": "cloud_ready" if OLLAMA_AVAILABLE else "not_ready",
            "models": {
                "llama3.2:3b": {
                    "model_id": "llama3.2:3b",
                    "model_name": "Llama 3.2 3B",
                    "is_loaded": "llama3.2:3b" in available_models,
                    "device": "cloud",
                    "cuda_available": False,
                    "load_time": 0,
                    "last_used": 0,
                    "error_count": 0,
                    "avg_response_time": 0
                },
                "codellama:7b": {
                    "model_id": "codellama:7b",
                    "model_name": "Code Llama 7B",
                    "is_loaded": "codellama:7b" in available_models,
                    "device": "cloud",
                    "cuda_available": False,
                    "load_time": 0,
                    "last_used": 0,
                    "error_count": 0,
                    "avg_response_time": 0
                }
            }
        },
        "models": {
            "llama3.2:3b": {
                "model_id": "llama3.2:3b",
                "model_name": "Llama 3.2 3B",
                "is_loaded": "llama3.2:3b" in available_models,
                "device": "cloud",
                "cuda_available": False,
                "load_time": 0,
                "last_used": 0,
                "error_count": 0,
                "avg_response_time": 0
            },
            "codellama:7b": {
                "model_id": "codellama:7b",
                "model_name": "Code Llama 7B",
                "is_loaded": "codellama:7b" in available_models,
                "device": "cloud",
                "cuda_available": False,
                "load_time": 0,
                "last_used": 0,
                "error_count": 0,
                "avg_response_time": 0
            }
        }
    }

@app.post("/api/models/{model_id}/initialize")
async def initialize_model(model_id: str):
    """Initialize a specific model"""
    try:
        # Check if models are downloaded
        if not MODELS_DOWNLOADED:
            return {
                "status": "downloading",
                "message": f"Models are being downloaded to Railway",
                "model_id": model_id,
                "available": False,
                "deployment": "cloud-only"
            }
        
        available_models = get_available_models()
        model_mapping = {
            "ethos-light": "llama3.2:3b",
            "ethos-code": "codellama:7b"
        }
        
        ollama_model = model_mapping.get(model_id, "llama3.2:3b")
        
        if ollama_model in available_models:
            return {
                "status": "success",
                "message": f"Model {model_id} ready on Railway",
                "model_id": model_id,
                "available": True,
                "deployment": "cloud-only"
            }
        else:
            return {
                "status": "error",
                "message": f"Model {model_id} not available",
                "model_id": model_id,
                "available": False,
                "deployment": "cloud-only"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to initialize model {model_id}: {str(e)}",
            "model_id": model_id,
            "available": False,
            "deployment": "cloud-only"
        }

@app.get("/api/models/{model_id}/status")
async def get_model_status(model_id: str):
    """Get status of a specific model"""
    try:
        available_models = get_available_models()
        model_mapping = {
            "ethos-light": "llama3.2:3b",
            "ethos-code": "codellama:7b"
        }
        
        ollama_model = model_mapping.get(model_id, "llama3.2:3b")
        
        return {
            "model_id": model_id,
            "status": "available" if ollama_model in available_models else "unavailable",
            "available": ollama_model in available_models,
            "deployment": "cloud-only"
        }
        
    except Exception as e:
        return {
            "model_id": model_id,
            "status": "error",
            "available": False,
            "error": str(e),
            "deployment": "cloud-only"
        }

@app.post("/api/conversations")
async def create_conversation():
    """Create a new conversation"""
    conversation_id = f"conv_{int(time.time())}"
    return {
        "conversation_id": conversation_id,
        "status": "created",
        "deployment": "cloud-only"
    }

@app.get("/api/conversations")
async def get_conversations():
    """Get all conversations"""
    return {
        "conversations": [],
        "deployment": "cloud-only"
    }

@app.get("/api/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get a specific conversation"""
    return {
        "id": conversation_id,
        "title": "Conversation",
        "messages": [],
        "deployment": "cloud-only"
    }

@app.get("/api/test-ollama")
async def test_ollama_endpoint():
    """Test Ollama and download models"""
    try:
        # Test Ollama
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            return {
                "status": "error",
                "message": "Ollama not available",
                "error": result.stderr,
                "deployment": "cloud-only"
            }
        
        ollama_version = result.stdout.strip()
        
        # List current models
        list_result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        current_models = list_result.stdout if list_result.returncode == 0 else "Error listing models"
        
        # Try to download 3B model
        download_result = subprocess.run(
            ['ollama', 'pull', 'llama3.2:3b'],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes for test
        )
        
        download_success = download_result.returncode == 0
        
        return {
            "status": "success",
            "ollama_version": ollama_version,
            "current_models": current_models,
            "download_success": download_success,
            "download_output": download_result.stdout if download_success else download_result.stderr,
            "deployment": "cloud-only"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Test failed: {str(e)}",
            "deployment": "cloud-only"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
