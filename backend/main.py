#!/usr/bin/env python3
"""
Ethos AI - Multi-Model System with Device Memory
VERSION: 5.0.0-MULTI-MODEL-MEMORY
DEPLOYMENT: DEVICE-MEMORY-SYSTEM
OLLAMA-INSTALLATION: MANUAL
MODELS: phi:1b, sailor2:1b, llama2:1b, llama3.2:3b, codellama:7b
FEATURES: Device memory, smart model selection, device linking API
"""

import os
import time
import json
import subprocess
import requests
import hashlib
import uuid
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
from typing import Optional, Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Ethos AI - Multi-Model System", version="5.0.0-MULTI-MODEL-MEMORY")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
OLLAMA_AVAILABLE = False
DOWNLOAD_IN_PROGRESS = False

# Device memory storage (in-memory for now, could be file-based)
DEVICE_MEMORIES = {}  # device_id -> memory_data
DEVICE_LINKS = {}     # device_id -> linked_device_ids

# Model configuration
MODELS = {
    "ethos-phi": {
        "name": "Ethos Phi (1B)",
        "ollama_model": "phi:1b",
        "size": "1.1 GB",
        "capabilities": ["programming", "debugging", "code_generation"],
        "best_for": ["coding", "technical", "programming"],
        "priority": 1
    },
    "ethos-sailor": {
        "name": "Ethos Sailor (1B)", 
        "ollama_model": "sailor2:1b",
        "size": "1.1 GB",
        "capabilities": ["general_knowledge", "multilingual", "conversation"],
        "best_for": ["general", "conversation", "multilingual"],
        "priority": 2
    },
    "ethos-fast": {
        "name": "Ethos Fast (1B)",
        "ollama_model": "llama2:1b", 
        "size": "1.2 GB",
        "capabilities": ["fast_responses", "general_knowledge"],
        "best_for": ["quick", "fast", "simple"],
        "priority": 3
    },
    "ethos-light": {
        "name": "Ethos Light (3B)",
        "ollama_model": "llama3.2:3b",
        "size": "3.4 GB", 
        "capabilities": ["better_quality", "reasoning", "analysis"],
        "best_for": ["quality", "analysis", "reasoning"],
        "priority": 4
    },
    "ethos-code": {
        "name": "Ethos Code (7B)",
        "ollama_model": "codellama:7b",
        "size": "7.2 GB",
        "capabilities": ["advanced_coding", "complex_programming", "best_quality"],
        "best_for": ["complex_coding", "advanced", "best_quality"],
        "priority": 5
    }
}

# Check if Ollama is available
def check_ollama_availability():
    """Check if Ollama is available without installing"""
    global OLLAMA_AVAILABLE
    try:
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"✅ Ollama available: {result.stdout.strip()}")
            OLLAMA_AVAILABLE = True
            return True
        else:
            logger.warning(f"⚠️ Ollama not available: {result.stderr}")
            OLLAMA_AVAILABLE = False
            return False
    except Exception as e:
        logger.warning(f"⚠️ Ollama not available: {e}")
        OLLAMA_AVAILABLE = False
        return False

# On-demand model download
def download_model_on_demand(model_name):
    """Download a specific model on-demand"""
    global DOWNLOAD_IN_PROGRESS
    
    if DOWNLOAD_IN_PROGRESS:
        return False
    
    DOWNLOAD_IN_PROGRESS = True
    logger.info(f"📥 Downloading {model_name} on-demand...")
    
    try:
        result = subprocess.run(
            ['ollama', 'pull', model_name],
            capture_output=True,
            text=True,
            timeout=1800  # 30 minutes
        )
        
        if result.returncode == 0:
            logger.info(f"✅ {model_name} downloaded successfully")
            DOWNLOAD_IN_PROGRESS = False
            return True
        else:
            logger.error(f"❌ Failed to download {model_name}: {result.stderr}")
            DOWNLOAD_IN_PROGRESS = False
            return False
            
    except Exception as e:
        logger.error(f"❌ Error downloading {model_name}: {e}")
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

# Device memory management
class DeviceMemory:
    """Device-local memory system"""
    
    def __init__(self, device_id: str):
        self.device_id = device_id
        self.conversations = []
        self.context = []
        self.settings = {}
        
    def add_conversation(self, conversation_id: str, message: str, response: str, model: str):
        """Add a conversation to device memory"""
        conversation = {
            "id": conversation_id,
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "response": response,
            "model": model
        }
        self.conversations.append(conversation)
        
        # Add to context for AI
        self.context.append({
            "role": "user",
            "content": message,
            "timestamp": conversation["timestamp"]
        })
        self.context.append({
            "role": "assistant", 
            "content": response,
            "timestamp": conversation["timestamp"]
        })
        
        # Keep only last 50 conversations to manage memory
        if len(self.conversations) > 50:
            self.conversations = self.conversations[-50:]
            self.context = self.context[-100:]  # Keep last 100 messages
    
    def get_recent_context(self, limit: int = 10) -> List[Dict]:
        """Get recent conversation context for AI"""
        return self.context[-limit:] if self.context else []
    
    def get_conversation_history(self, limit: int = 20) -> List[Dict]:
        """Get conversation history"""
        return self.conversations[-limit:] if self.conversations else []
    
    def get_linked_device_context(self, linked_device_ids: List[str]) -> List[Dict]:
        """Get context from linked devices"""
        linked_context = []
        for device_id in linked_device_ids:
            if device_id in DEVICE_MEMORIES:
                linked_context.extend(DEVICE_MEMORIES[device_id].get_recent_context(5))
        return linked_context

def get_or_create_device_memory(device_id: str) -> DeviceMemory:
    """Get or create device memory"""
    if device_id not in DEVICE_MEMORIES:
        DEVICE_MEMORIES[device_id] = DeviceMemory(device_id)
    return DEVICE_MEMORIES[device_id]

# Smart model selection
class SmartModelSelector:
    """Intelligent model selection based on task and available resources"""
    
    def __init__(self):
        self.current_loaded_model = None
        self.model_usage_stats = {}
        
    def select_best_model(self, user_message: str, available_models: List[str]) -> str:
        """Select the best model for the given task"""
        user_message_lower = user_message.lower()
        
        # Check for coding-related keywords
        coding_keywords = ["code", "program", "function", "bug", "error", "python", "javascript", 
                          "html", "css", "java", "c++", "debug", "algorithm", "api", "database",
                          "class", "method", "variable", "loop", "if", "else", "try", "catch"]
        
        # Check for complex tasks
        complex_keywords = ["analyze", "explain", "compare", "evaluate", "design", "architecture",
                           "optimize", "performance", "security", "scalability"]
        
        # Check for simple/quick tasks
        simple_keywords = ["hello", "hi", "thanks", "ok", "yes", "no", "quick", "simple"]
        
        # Priority-based selection
        if any(keyword in user_message_lower for keyword in coding_keywords):
            # Try 7B first, then 3B, then 1B models
            for model_id in ["ethos-code", "ethos-light", "ethos-phi"]:
                if MODELS[model_id]["ollama_model"] in available_models:
                    return model_id
        
        elif any(keyword in user_message_lower for keyword in complex_keywords):
            # Try 3B first, then 7B, then 1B
            for model_id in ["ethos-light", "ethos-code", "ethos-sailor"]:
                if MODELS[model_id]["ollama_model"] in available_models:
                    return model_id
        
        elif any(keyword in user_message_lower for keyword in simple_keywords):
            # Use fast 1B model
            for model_id in ["ethos-fast", "ethos-sailor", "ethos-phi"]:
                if MODELS[model_id]["ollama_model"] in available_models:
                    return model_id
        
        # Default: try best available model
        for model_id in ["ethos-code", "ethos-light", "ethos-sailor", "ethos-phi", "ethos-fast"]:
            if MODELS[model_id]["ollama_model"] in available_models:
                return model_id
        
        # Fallback to any available model
        for model_id, model_info in MODELS.items():
            if model_info["ollama_model"] in available_models:
                return model_id
        
        return "ethos-phi"  # Default fallback
    
    def load_model(self, model_id: str) -> bool:
        """Load a specific model"""
        try:
            model_info = MODELS.get(model_id)
            if not model_info:
                return False
                
            ollama_model = model_info["ollama_model"]
            
            # Check if model is available
            available_models = get_available_models()
            if ollama_model not in available_models:
                logger.info(f"📥 Model {ollama_model} not found, downloading on-demand...")
                if not download_model_on_demand(ollama_model):
                    return False
            
            if self.current_loaded_model == ollama_model:
                logger.info(f"✅ Model {ollama_model} already loaded")
                return True
            
            # Unload current model if different
            if self.current_loaded_model and self.current_loaded_model != ollama_model:
                logger.info(f"🔄 Unloading {self.current_loaded_model} to save memory")
                try:
                    subprocess.run(['pkill', '-f', 'ollama'], capture_output=True)
                    time.sleep(2)
                except:
                    pass
            
            logger.info(f"🚀 Loading model: {ollama_model}")
            try:
                # Start the model in background
                subprocess.Popen(['ollama', 'run', ollama_model], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
                time.sleep(3)  # Wait for model to load
                self.current_loaded_model = ollama_model
                return True
            except Exception as e:
                logger.error(f"❌ Failed to load model {ollama_model}: {e}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error in load_model: {e}")
            return False
    
    def generate_response(self, prompt: str, model_id: str, device_context: List[Dict] = None) -> str:
        """Generate response using the specified model with context"""
        try:
            # Load the model
            if not self.load_model(model_id):
                raise Exception(f"Failed to load model {model_id}")
            
            model_info = MODELS.get(model_id)
            if not model_info:
                raise Exception(f"Unknown model {model_id}")
            
            ollama_model = model_info["ollama_model"]
            
            # Build context-aware prompt
            full_prompt = self._build_context_prompt(prompt, device_context)
            
            # Generate response
            result = subprocess.run(
                ['ollama', 'run', ollama_model, full_prompt],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                raise Exception(f"Model generation failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"❌ Error generating response: {e}")
            raise e
    
    def _build_context_prompt(self, prompt: str, device_context: List[Dict] = None) -> str:
        """Build a context-aware prompt"""
        if not device_context:
            return prompt
        
        # Build context from device memory
        context_text = "\n\nPrevious conversation context:\n"
        for item in device_context[-10:]:  # Last 10 context items
            role = item.get("role", "user")
            content = item.get("content", "")
            if content:
                context_text += f"{role.capitalize()}: {content}\n"
        
        context_text += f"\nCurrent message: {prompt}\n\nPlease respond to the current message, taking into account the conversation context above."
        
        return context_text

# Initialize components
smart_selector = SmartModelSelector()
check_ollama_availability()

# API Models
class ChatRequest(BaseModel):
    message: str
    device_id: str
    model_override: Optional[str] = None
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    model: str
    device_id: str
    conversation_id: str
    deployment: str
    context_used: bool

class DeviceLinkRequest(BaseModel):
    device_id: str
    target_device_id: str

class DeviceLinkResponse(BaseModel):
    status: str
    message: str
    linked_devices: List[str]

# API Endpoints
@app.get("/")
async def root():
    available_models = get_available_models() if OLLAMA_AVAILABLE else []
    return {
        "message": "Ethos AI - Multi-Model System with Device Memory",
        "status": "healthy",
        "version": "5.0.0-MULTI-MODEL-MEMORY",
        "ollama_available": OLLAMA_AVAILABLE,
        "download_in_progress": DOWNLOAD_IN_PROGRESS,
        "available_models": available_models,
        "deployment": "device-memory-system",
        "build": "MULTI-MODEL-MEMORY",
        "features": ["device_memory", "smart_model_selection", "device_linking", "multi_model"]
    }

@app.get("/health")
async def health_check():
    available_models = get_available_models() if OLLAMA_AVAILABLE else []
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "5.0.0-MULTI-MODEL-MEMORY",
        "ollama_available": OLLAMA_AVAILABLE,
        "download_in_progress": DOWNLOAD_IN_PROGRESS,
        "available_models": available_models,
        "deployment": "device-memory-system",
        "active_devices": len(DEVICE_MEMORIES),
        "device_links": len(DEVICE_LINKS)
    }

@app.get("/api/models")
async def get_models():
    """Get available models with smart selection info"""
    try:
        if OLLAMA_AVAILABLE:
            available_models = get_available_models()
            
            # Create model list with availability status
            ethos_models = []
            for model_id, model_info in MODELS.items():
                is_available = model_info["ollama_model"] in available_models
                ethos_models.append({
                    "id": model_id,
                    "name": model_info["name"],
                    "type": "cloud",
                    "provider": "ollama",
                    "enabled": True,
                    "status": "available" if is_available else "downloadable",
                    "ollama_model": model_info["ollama_model"],
                    "capabilities": model_info["capabilities"],
                    "best_for": model_info["best_for"],
                    "size": model_info["size"],
                    "priority": model_info["priority"],
                    "fusion_capable": False,
                    "reason": f"Smart selection model - {', '.join(model_info['best_for'])}"
                })
            
            return {
                "models": ethos_models,
                "deployment": "device-memory-system",
                "total": len(ethos_models),
                "smart_selection": True,
                "device_memory": True
            }
        else:
            return {
                "models": [],
                "error": "Ollama not available",
                "deployment": "device-memory-system"
            }
            
    except Exception as e:
        return {
            "models": [],
            "error": str(e),
            "deployment": "device-memory-system"
        }

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Chat endpoint with device memory and smart model selection"""
    try:
        if not OLLAMA_AVAILABLE:
            raise HTTPException(
                status_code=503,
                detail="Ollama not available"
            )
        
        # Get or create device memory
        device_memory = get_or_create_device_memory(request.device_id)
        
        # Get device context (including linked devices)
        linked_devices = DEVICE_LINKS.get(request.device_id, [])
        device_context = device_memory.get_recent_context(10)
        linked_context = device_memory.get_linked_device_context(linked_devices)
        
        # Combine contexts
        full_context = device_context + linked_context
        context_used = len(full_context) > 0
        
        # Smart model selection
        available_models = get_available_models()
        if request.model_override and request.model_override in MODELS:
            selected_model = request.model_override
        else:
            selected_model = smart_selector.select_best_model(request.message, available_models)
        
        # Generate response
        response = smart_selector.generate_response(
            request.message, 
            selected_model, 
            full_context
        )
        
        # Store in device memory
        conversation_id = request.conversation_id or f"conv_{int(time.time())}"
        device_memory.add_conversation(
            conversation_id,
            request.message,
            response,
            selected_model
        )
        
        return ChatResponse(
            response=response,
            model=selected_model,
            device_id=request.device_id,
            conversation_id=conversation_id,
            deployment="device-memory-system",
            context_used=context_used
        )
        
    except Exception as e:
        logger.error(f"❌ Chat error: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Chat error: {str(e)}"
        )

@app.get("/api/device/{device_id}/memory")
async def get_device_memory(device_id: str, limit: int = 20):
    """Get device memory/conversation history"""
    try:
        device_memory = get_or_create_device_memory(device_id)
        conversations = device_memory.get_conversation_history(limit)
        
        return {
            "device_id": device_id,
            "conversations": conversations,
            "total_conversations": len(device_memory.conversations),
            "deployment": "device-memory-system"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/device/link", response_model=DeviceLinkResponse)
async def link_devices(request: DeviceLinkRequest):
    """Link two devices for shared context"""
    try:
        # Create device memories if they don't exist
        get_or_create_device_memory(request.device_id)
        get_or_create_device_memory(request.target_device_id)
        
        # Link devices (bidirectional)
        if request.device_id not in DEVICE_LINKS:
            DEVICE_LINKS[request.device_id] = []
        if request.target_device_id not in DEVICE_LINKS:
            DEVICE_LINKS[request.target_device_id] = []
        
        if request.target_device_id not in DEVICE_LINKS[request.device_id]:
            DEVICE_LINKS[request.device_id].append(request.target_device_id)
        if request.device_id not in DEVICE_LINKS[request.target_device_id]:
            DEVICE_LINKS[request.target_device_id].append(request.device_id)
        
        return DeviceLinkResponse(
            status="success",
            message=f"Devices {request.device_id} and {request.target_device_id} linked successfully",
            linked_devices=DEVICE_LINKS[request.device_id]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/device/link")
async def unlink_devices(request: DeviceLinkRequest):
    """Unlink two devices"""
    try:
        if request.device_id in DEVICE_LINKS and request.target_device_id in DEVICE_LINKS[request.device_id]:
            DEVICE_LINKS[request.device_id].remove(request.target_device_id)
        if request.target_device_id in DEVICE_LINKS and request.device_id in DEVICE_LINKS[request.target_device_id]:
            DEVICE_LINKS[request.target_device_id].remove(request.device_id)
        
        return {
            "status": "success",
            "message": f"Devices {request.device_id} and {request.target_device_id} unlinked"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/device/{device_id}/links")
async def get_device_links(device_id: str):
    """Get linked devices for a device"""
    try:
        linked_devices = DEVICE_LINKS.get(device_id, [])
        return {
            "device_id": device_id,
            "linked_devices": linked_devices,
            "total_linked": len(linked_devices)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/download-model")
async def download_model_endpoint(model_name: str):
    """Download a specific model on-demand"""
    try:
        if not OLLAMA_AVAILABLE:
            raise HTTPException(status_code=503, detail="Ollama not available")
        
        if DOWNLOAD_IN_PROGRESS:
            return {
                "status": "in_progress",
                "message": "Another download is already in progress",
                "deployment": "device-memory-system"
            }
        
        # Validate model name
        valid_models = [model_info["ollama_model"] for model_info in MODELS.values()]
        if model_name not in valid_models:
            raise HTTPException(status_code=400, detail=f"Invalid model. Must be one of: {valid_models}")
        
        # Check if already downloaded
        available_models = get_available_models()
        if model_name in available_models:
            return {
                "status": "already_downloaded",
                "message": f"{model_name} is already available",
                "deployment": "device-memory-system"
            }
        
        # Start download
        success = download_model_on_demand(model_name)
        
        if success:
            return {
                "status": "success",
                "message": f"{model_name} downloaded successfully",
                "deployment": "device-memory-system"
            }
        else:
            raise HTTPException(status_code=500, detail=f"Failed to download {model_name}")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download error: {str(e)}")

@app.get("/api/test-ollama")
async def test_ollama_endpoint():
    """Test Ollama and show available models"""
    try:
        # Test Ollama
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            return {
                "status": "error",
                "message": "Ollama not available",
                "error": result.stderr,
                "deployment": "device-memory-system"
            }
        
        ollama_version = result.stdout.strip()
        
        # List current models
        list_result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        current_models = list_result.stdout if list_result.returncode == 0 else "Error listing models"
        
        # Check model availability
        available_models = get_available_models()
        model_status = {}
        for model_id, model_info in MODELS.items():
            model_status[model_id] = model_info["ollama_model"] in available_models
        
        return {
            "status": "success",
            "ollama_version": ollama_version,
            "current_models": current_models,
            "model_status": model_status,
            "download_in_progress": DOWNLOAD_IN_PROGRESS,
            "deployment": "device-memory-system",
            "active_devices": len(DEVICE_MEMORIES),
            "device_links": len(DEVICE_LINKS)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Test failed: {str(e)}",
            "deployment": "device-memory-system"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
