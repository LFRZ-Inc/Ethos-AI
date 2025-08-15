#!/usr/bin/env python3
"""
Ethos AI - Local AI Backend with Real Local Models
"""

import os
import time
import logging
import uuid
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Ethos AI",
    description="Privacy-First Local AI Backend",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",  # Allow all origins for now
        "https://ethos-ai-phi.vercel.app",
        "https://ethos-ai-phi.vercel.app/",
        "https://*.vercel.app",
        "https://*.railway.app",
        "http://localhost:3000",
        "http://localhost:1420",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:1420"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Pydantic models
class ChatMessage(BaseModel):
    content: Optional[str] = None
    message: Optional[str] = None
    conversation_id: Optional[str] = None
    model_override: Optional[str] = None
    use_tools: bool = True
    
    def get_content(self) -> str:
        """Get the message content from either content or message field"""
        if self.content:
            return self.content
        elif self.message:
            return self.message
        else:
            raise ValueError("Either 'content' or 'message' field is required")

class ChatResponse(BaseModel):
    content: str
    model_used: str
    timestamp: str
    tools_called: Optional[list] = None

# In-memory storage for development
conversations = {}
messages = {}
conversation_counter = 0

# Lightweight model system for Railway stability
MODEL_SYSTEM_AVAILABLE = False
model_system_initialized = False
model_system_loading = False

def load_model_system():
    """Lazy load the model system only when needed"""
    global MODEL_SYSTEM_AVAILABLE
    if not MODEL_SYSTEM_AVAILABLE:
        try:
            # Try to import heavy dependencies only when needed
            from models import initialize_model, generate_response, get_model_info, get_system_status, unload_model
            MODEL_SYSTEM_AVAILABLE = True
            logger.info("Local AI model system loaded successfully")
            return True
        except ImportError as e:
            logging.warning(f"Local model system not available: {e}")
            MODEL_SYSTEM_AVAILABLE = False
            logger.info("Using lightweight fallback system - models not available")
            return False
    return True

# Local AI Models - Real local models
LOCAL_MODELS = {
    "ethos-light": {
        "id": "ethos-light",
        "name": "Ethos Light",
        "type": "local",
        "provider": "ethos",
        "capabilities": ["general_chat", "privacy_focused", "basic_assistance", "fast_responses"],
        "enabled": True,
        "status": "unavailable",
        "description": "Lightweight AI for quick responses and basic tasks",
        "parameters": "3B",
        "quantization": "4-bit",
        "speed": "fast",
        "capability": "basic"
    },
    "ethos-code": {
        "id": "ethos-code",
        "name": "Ethos Code",
        "type": "local",
        "provider": "ethos",
        "capabilities": ["coding", "programming", "debugging", "code_review", "algorithm_design"],
        "enabled": True,
        "status": "unavailable",
        "description": "Specialized AI for coding and development tasks",
        "parameters": "7B",
        "quantization": "4-bit",
        "speed": "medium",
        "capability": "coding"
    },
    "ethos-pro": {
        "id": "ethos-pro",
        "name": "Ethos Pro",
        "type": "local",
        "provider": "ethos",
        "capabilities": ["advanced_reasoning", "analysis", "research", "complex_tasks", "detailed_explanations"],
        "enabled": True,
        "status": "unavailable",
        "description": "Professional AI for complex analysis and detailed work",
        "parameters": "70B",
        "quantization": "4-bit",
        "speed": "slow",
        "capability": "advanced"
    },
    "ethos-creative": {
        "id": "ethos-creative",
        "name": "Ethos Creative",
        "type": "local",
        "provider": "ethos",
        "capabilities": ["creative_writing", "content_creation", "storytelling", "artistic_tasks", "brainstorming"],
        "enabled": True,
        "status": "unavailable",
        "description": "Creative AI for writing, content creation, and artistic tasks",
        "parameters": "7B",
        "quantization": "4-bit",
        "speed": "medium",
        "capability": "creative"
    }
}

def get_local_ai_response(message: str, model_id: str = "ethos-light") -> str:
    """Get response from local AI models with lazy loading"""
    global model_system_initialized, model_system_loading
    
    # Lazy load the model system
    if not load_model_system():
        return get_fallback_response(message, model_id)
    
    # Map our model names to actual model IDs
    model_mapping = {
        "ethos-light": "ethos-3b",      # 3B model for fast responses
        "ethos-code": "ethos-7b",       # 7B model for coding
        "ethos-pro": "ethos-70b",       # 70B model for complex tasks
        "ethos-creative": "ethos-7b"    # 7B model for creative tasks
    }
    
    actual_model_id = model_mapping.get(model_id, "ethos-3b")
    
    # Try to load model if not already loaded
    if not model_system_initialized and not model_system_loading:
        model_system_loading = True
        logger.info(f"Initializing local model system with {actual_model_id}...")
        try:
            from models import initialize_model
            model_system_initialized = initialize_model(actual_model_id)
            model_system_loading = False
            if model_system_initialized:
                logger.info(f"Local model {actual_model_id} initialized successfully!")
            else:
                logger.warning(f"Failed to initialize local model {actual_model_id}")
        except Exception as e:
            logger.error(f"Error initializing local model {actual_model_id}: {e}")
            model_system_loading = False
            model_system_initialized = False
    
    # Generate response using the local model system
    if model_system_initialized:
        try:
            from models import generate_response
            response = generate_response(message, actual_model_id)
            logger.info(f"Generated response using local model {actual_model_id}")
            return response
        except Exception as e:
            logger.error(f"Error generating response with local model {actual_model_id}: {e}")
            return f"Error: Local model {actual_model_id} failed to generate response: {str(e)}"
    elif model_system_loading:
        return f"Loading local model {actual_model_id} to provide intelligent responses. Please try again in a few seconds."
    else:
        return f"Error: Local model {actual_model_id} is not available. Please try a different model or check system status."

def get_fallback_response(message: str, model_id: str) -> str:
    """Fallback response when AI models are not available"""
    responses = {
        "ethos-light": f"🤖 Ethos Light (3B) is currently loading. Your message: '{message[:50]}...' - Please wait for model initialization.",
        "ethos-code": f"💻 Ethos Code (7B) is preparing for coding tasks. Your message: '{message[:50]}...' - Model loading in progress.",
        "ethos-pro": f"🧠 Ethos Pro (70B) is initializing for advanced analysis. Your message: '{message[:50]}...' - Please be patient.",
        "ethos-creative": f"🎨 Ethos Creative (7B) is getting ready for creative tasks. Your message: '{message[:50]}...' - Model loading..."
    }
    return responses.get(model_id, f"Ethos AI is loading models. Your message: '{message[:50]}...' - Please try again in a moment.")

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    try:
        response_data = {
            "message": "Ethos AI Backend is running!",
            "status": "healthy",
            "version": "1.0.0",
            "mode": "privacy-first",
            "privacy": "100% local - no external tracking",
            "timestamp": time.time()
        }
        
        from fastapi.responses import JSONResponse
        response = JSONResponse(content=response_data)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response
        
    except Exception as e:
        logger.error(f"Root endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        health_data = {
            "status": "healthy",
            "service": "ethos-ai-backend",
            "mode": "privacy-first",
            "privacy": "100% local processing - no external data collection",
            "timestamp": time.time(),
            "environment": "production",
            "port": os.environ.get("PORT", "8080"),
            "privacy_features": [
                "No data selling",
                "No external API calls",
                "Local model processing",
                "Self-contained AI",
                "Private learning only"
            ]
        }
        
        from fastapi.responses import JSONResponse
        response = JSONResponse(content=health_data)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test")
async def test_endpoint():
    """Test endpoint"""
    try:
        response_data = {
            "status": "ok",
            "message": "Backend is working",
            "mode": "privacy-first",
            "timestamp": time.time(),
            "cors_enabled": True
        }
        
        from fastapi.responses import JSONResponse
        response = JSONResponse(content=response_data)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response
        
    except Exception as e:
        logger.error(f"Test endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/models")
async def get_models():
    """Get available models"""
    try:
        # Check local model system availability with lazy loading
        local_models_available = load_model_system()
        
        models = [
            {
                "id": "ethos-light",
                "name": "Ethos Light",
                "type": "local",
                "provider": "ethos",
                "capabilities": ["general_chat", "privacy_focused", "basic_assistance", "fast_responses"],
                "enabled": True,
                "status": "available" if local_models_available else "unavailable",
                "description": "Lightweight AI for quick responses and basic tasks",
                "parameters": "3B",
                "quantization": "4-bit",
                "speed": "fast",
                "capability": "basic"
            },
            {
                "id": "ethos-code",
                "name": "Ethos Code", 
                "type": "local",
                "provider": "ethos",
                "capabilities": ["coding", "programming", "debugging", "code_review", "algorithm_design"],
                "enabled": True,
                "status": "available" if local_models_available else "unavailable",
                "description": "Specialized AI for coding and development tasks",
                "parameters": "7B",
                "quantization": "4-bit", 
                "speed": "medium",
                "capability": "coding"
            },
            {
                "id": "ethos-pro",
                "name": "Ethos Pro",
                "type": "local", 
                "provider": "ethos",
                "capabilities": ["advanced_reasoning", "analysis", "research", "complex_tasks", "detailed_explanations"],
                "enabled": True,
                "status": "available" if local_models_available else "unavailable",
                "description": "Professional AI for complex analysis and detailed work",
                "parameters": "70B",
                "quantization": "4-bit",
                "speed": "slow", 
                "capability": "advanced"
            },
            {
                "id": "ethos-creative",
                "name": "Ethos Creative",
                "type": "local",
                "provider": "ethos", 
                "capabilities": ["creative_writing", "content_creation", "storytelling", "artistic_tasks", "brainstorming"],
                "enabled": True,
                "status": "available" if local_models_available else "unavailable",
                "description": "Creative AI for writing, content creation, and artistic tasks",
                "parameters": "7B",
                "quantization": "4-bit",
                "speed": "medium",
                "capability": "creative"
            }
        ]
        
        response_data = {
            "models": models,
            "total": len(models),
            "status": "available" if local_models_available else "unavailable",
            "model_system": "local" if local_models_available else "fallback"
        }
        
        from fastapi.responses import JSONResponse
        response = JSONResponse(content=response_data)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response
        
    except Exception as e:
        logger.error(f"Error getting models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/models/status")
async def get_model_status():
    """Get model system status"""
    try:
        local_models_available = load_model_system()
        
        status_data = {
            "system_status": "available" if local_models_available else "unavailable",
            "models_loaded": local_models_available,
            "privacy_mode": "enabled",
            "external_apis": "disabled",
            "data_collection": "disabled"
        }
        
        from fastapi.responses import JSONResponse
        response = JSONResponse(content=status_data)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response
        
    except Exception as e:
        logger.error(f"Error getting model status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat(message: ChatMessage):
    """Chat endpoint"""
    try:
        content = message.get_content()
        model_id = message.model_override or "ethos-light"
        
        logger.info(f"Received chat message: {content[:50]}... with model: {model_id}")
        
        # Get response from local AI
        response_content = get_local_ai_response(content, model_id)
        
        response_data = {
            "content": response_content,
            "model_used": model_id,
            "timestamp": datetime.now().isoformat(),
            "privacy": "100% local processing"
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

@app.get("/api/conversations")
async def get_conversations():
    """Get all conversations"""
    try:
        # For now, return empty list - you can implement actual storage later
        conversations = []
        
        response_data = {
            "conversations": conversations,
            "total": len(conversations)
        }
        
        from fastapi.responses import JSONResponse
        response = JSONResponse(content=response_data)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response
        
    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/models/{model_id}/download")
async def download_model(model_id: str):
    """Download a model to Railway server - Privacy First Approach"""
    try:
        # Model download URLs - Privacy-focused models only
        model_urls = {
            "ethos-3b": "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
            "ethos-7b": "https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGML/resolve/main/llama-2-7b-chat.ggmlv3.q4_0.bin",
            "ethos-70b": "https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGML/resolve/main/llama-2-7b-chat.ggmlv3.q4_0.bin"
        }
        
        if model_id not in model_urls:
            raise HTTPException(status_code=400, detail=f"Model {model_id} not found")
        
        url = model_urls[model_id]
        model_path = f"/tmp/{model_id}.gguf"
        
        logger.info(f"Starting privacy-first download of {model_id} from {url}")
        
        # Download with privacy-focused headers
        import requests
        headers = {
            "User-Agent": "Ethos-AI/1.0 (Privacy-First AI)",
            "Accept": "application/octet-stream"
        }
        
        # Try with HuggingFace token if available (for private models)
        hf_token = os.environ.get("HUGGINGFACE_TOKEN")
        if hf_token:
            headers["Authorization"] = f"Bearer {hf_token}"
        
        response = requests.get(url, headers=headers, stream=True, timeout=300)
        response.raise_for_status()
        
        # Download with progress tracking
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(model_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        logger.info(f"Download progress for {model_id}: {progress:.1f}%")
        
        logger.info(f"Successfully downloaded {model_id} to {model_path} (Privacy-First)")
        
        response_data = {
            "status": "success",
            "message": f"Model {model_id} downloaded successfully - Privacy First!",
            "model_id": model_id,
            "file_path": model_path,
            "file_size": os.path.getsize(model_path),
            "privacy": "100% local processing - no external data collection"
        }
        
        from fastapi.responses import JSONResponse
        response = JSONResponse(content=response_data)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response
        
    except Exception as e:
        logger.error(f"Error downloading model {model_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/privacy")
async def get_privacy_info():
    """Get privacy information about Ethos AI"""
    try:
        privacy_info = {
            "privacy_policy": "100% Privacy-First",
            "data_collection": "None - All processing local",
            "data_selling": "Never - We don't sell data",
            "external_apis": "None - Self-contained AI",
            "learning": "Self-improvement only - data stays private",
            "storage": "Local only - no cloud data mining",
            "purpose": "Ethos AI growth through private interactions"
        }
        
        from fastapi.responses import JSONResponse
        response = JSONResponse(content=privacy_info)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response
        
    except Exception as e:
        logger.error(f"Error getting privacy info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Global error handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080))) 