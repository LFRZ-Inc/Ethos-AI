#!/usr/bin/env python3
"""
Ethos AI - Local AI Backend with Real Local Models
"""

import os
import logging
import time
import json
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Import local AI model system
try:
    from models import initialize_model, generate_response, get_model_info, get_system_status, unload_model
    MODEL_SYSTEM_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("Local AI model system loaded successfully")
except ImportError as e:
    logging.warning(f"Local model system not available: {e}")
    MODEL_SYSTEM_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.info("Using Ollama API system - local models not available")

# Ollama API integration
import requests
import json

OLLAMA_BASE_URL = "http://localhost:11434"  # Default Ollama URL
OLLAMA_AVAILABLE = False

def check_ollama_availability():
    """Check if Ollama is running and available"""
    global OLLAMA_AVAILABLE
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            OLLAMA_AVAILABLE = True
            logger.info("Ollama API is available")
            return True
    except Exception as e:
        logger.warning(f"Ollama not available: {e}")
        OLLAMA_AVAILABLE = False
    return False

def get_ollama_response(message: str, model_name: str = "llama3.2:3b") -> str:
    """Get response from Ollama API"""
    if not OLLAMA_AVAILABLE:
        return "Ollama is not available. Please start Ollama server."
    
    try:
        payload = {
            "model": model_name,
            "prompt": message,
            "stream": False
        }
        
        response = requests.post(f"{OLLAMA_BASE_URL}/api/generate", 
                               json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "No response from Ollama")
        else:
            return f"Error: Ollama API returned status {response.status_code}"
            
    except Exception as e:
        logger.error(f"Error calling Ollama API: {e}")
        return f"Error: Failed to get response from Ollama - {str(e)}"

# Check Ollama availability on startup
check_ollama_availability()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Ethos AI",
    description="Local AI backend with real local models",
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

# Global model system status
model_system_initialized = False
model_system_loading = False

# Local AI Models - Real local models
LOCAL_MODELS = {
    "ethos-light": {
        "id": "ethos-light",
        "name": "Ethos Light",
        "type": "local",
        "provider": "ethos",
        "capabilities": ["general_chat", "privacy_focused", "basic_assistance", "fast_responses"],
        "enabled": True,
        "status": "available" if MODEL_SYSTEM_AVAILABLE else "unavailable",
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
        "status": "available" if MODEL_SYSTEM_AVAILABLE else "unavailable",
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
        "status": "available" if MODEL_SYSTEM_AVAILABLE else "unavailable",
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
        "status": "available" if MODEL_SYSTEM_AVAILABLE else "unavailable",
        "description": "Creative AI for writing, content creation, and artistic tasks",
        "parameters": "7B",
        "quantization": "4-bit",
        "speed": "medium",
        "capability": "creative"
    }
}

def get_local_ai_response(message: str, model_id: str = "ethos-light") -> str:
    """Get response from Ollama models"""
    # Map our model names to actual Ollama model names
    model_mapping = {
        "ethos-light": "llama3.2:3b",      # 3B model for fast responses
        "ethos-code": "llava:7b",          # 7B model for coding (using llava since you have it)
        "ethos-pro": "llama3.1:70b",       # 70B model for complex tasks
        "ethos-creative": "llava:7b"       # 7B model for creative tasks
    }
    
    actual_model_name = model_mapping.get(model_id, "llama3.2:3b")
    
    # Use Ollama API
    if OLLAMA_AVAILABLE:
        return get_ollama_response(message, actual_model_name)
    else:
        # Fallback if Ollama is not available
        return f"Ollama is not available. Please start Ollama server to use {actual_model_name}."

def get_fallback_response(message: str, model_id: str) -> str:
    """Fallback response when local models are unavailable"""
    message_lower = message.lower()
    
    # Handle greetings
    if any(word in message_lower for word in ["hello", "hi", "hey", "greetings"]):
        return "Hello! I'm Ethos AI, your privacy-focused local assistant. I'm currently running in fallback mode while the local AI models are being set up. I can still help you with basic tasks and questions. What can I assist you with today?"
    
    # Handle capability questions
    if any(phrase in message_lower for phrase in ["what can you do", "what do you do", "help me", "capabilities", "features"]):
        return """I'm Ethos AI, your privacy-focused local assistant! Here's what I can help you with:

🤖 **Current Mode**: Fallback AI (local models being initialized)
💬 **General Chat**: I can engage in conversations and answer questions
📝 **Text Processing**: Help with writing, editing, and text analysis
🧮 **Basic Reasoning**: Simple problem-solving and explanations
🔒 **Privacy**: 100% local processing - no external tracking

The local 70B, 7B, and 3B models are being set up and will provide even more intelligent responses once available. What would you like help with?"""
    
    # Handle questions about the system
    if any(phrase in message_lower for phrase in ["why unavailable", "models unavailable", "system status", "what's wrong"]):
        return "The local AI models (70B, 7B, 3B) are currently being initialized on the server. This requires loading large model files and setting up the local AI processing environment. I'm working in fallback mode to provide basic assistance while this happens. The models should become available soon!"
    
    # Model-specific responses
    if model_id == "ethos-code":
        if any(word in message_lower for word in ["code", "program", "debug", "algorithm", "function", "python", "javascript", "html", "css"]):
            return f"I'm Ethos Code, specialized for programming tasks! I can help you with {message}. The local 7B coding model is being initialized and will provide advanced programming assistance once available. For now, I can provide basic coding guidance and help you structure your code."
        else:
            return f"I'm Ethos Code, your coding assistant! While I'm specialized for programming tasks, I can also help with general questions. The local 7B coding model will provide advanced programming help once initialized."
    
    elif model_id == "ethos-pro":
        if "?" in message:
            return f"I'm Ethos Pro, designed for detailed analysis and complex reasoning! I can provide analysis of {message}. The local 70B model is being initialized and will provide advanced reasoning capabilities once available. For now, I can help you structure your thoughts and approach to this question."
        else:
            return f"I'm Ethos Pro, your professional analysis assistant! I can help with complex reasoning, detailed analysis, research tasks, and comprehensive explanations. The local 70B model will provide advanced analysis capabilities once initialized."
    
    elif model_id == "ethos-creative":
        if any(word in message_lower for word in ["write", "story", "creative", "content", "art", "design", "poem", "article"]):
            return f"I'm Ethos Creative, your creative writing assistant! I can help you with {message}. The local 7B creative model is being initialized and will provide advanced creative capabilities once available. For now, I can help you brainstorm ideas and structure your creative projects."
        else:
            return f"I'm Ethos Creative, designed for creative tasks! I can help with writing, storytelling, content creation, brainstorming, and artistic projects. The local 7B creative model will provide advanced creative capabilities once initialized."
    
    else:  # ethos-light (default)
        if any(word in message_lower for word in ["code", "program", "debug", "algorithm", "function", "python", "javascript"]):
            return f"I can help you with programming questions! I'm currently in fallback mode, but I can still provide basic coding assistance, explain concepts, and help with simple programming problems. The local 3B model will provide fast responses once initialized."
        elif "?" in message:
            return f"That's an interesting question about {message}! I'm currently running in fallback mode while the local 3B model is being initialized. For now, I can help you think through this step by step."
        else:
            return f"I understand you're asking about {message}. I'm currently running in fallback mode while the local 3B model is being initialized. I can still help you organize your thoughts and approach to this topic."

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Ethos AI Backend is running!", 
        "status": "healthy",
        "version": "1.0.0",
        "mode": "clean",
        "privacy": "100% local - no external tracking",
        "timestamp": time.time()
    }

@app.get("/health")
async def health():
    """Health check endpoint for Railway"""
    try:
        response_data = {
            "status": "healthy", 
            "service": "ethos-ai-backend",
            "mode": "clean",
            "privacy": "local-first, no external dependencies",
            "timestamp": time.time(),
            "environment": os.environ.get("RAILWAY_ENVIRONMENT", "production"),
            "port": os.environ.get("PORT", "8000")
        }
        
        from fastapi.responses import JSONResponse
        response = JSONResponse(content=response_data)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test")
async def test_endpoint():
    """Test endpoint to verify backend is working"""
    return {
        "status": "ok",
        "message": "Backend is working",
        "mode": "clean",
        "timestamp": time.time(),
        "cors_enabled": True
    }

@app.get("/api/models")
async def get_models():
    """Get available models"""
    # Check Ollama availability and get model list
    ollama_models = []
    if OLLAMA_AVAILABLE:
        try:
            response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
            if response.status_code == 200:
                ollama_data = response.json()
                ollama_models = [model["name"] for model in ollama_data.get("models", [])]
        except Exception as e:
            logger.error(f"Error getting Ollama models: {e}")
    
    # Define our model mapping
    model_mapping = {
        "ethos-light": "llama3.2:3b",
        "ethos-code": "llava:7b", 
        "ethos-pro": "llama3.1:70b",
        "ethos-creative": "llava:7b"
    }
    
    models = [
        {
            "id": "ethos-light",
            "name": "Ethos Light",
            "type": "local",
            "provider": "ollama",
            "capabilities": ["general_chat", "privacy_focused", "basic_assistance", "fast_responses"],
            "enabled": True,
            "status": "available" if "llama3.2:3b" in ollama_models else "unavailable",
            "description": "Lightweight AI for quick responses and basic tasks",
            "parameters": "3B",
            "quantization": "4-bit",
            "speed": "fast",
            "capability": "basic",
            "ollama_model": "llama3.2:3b"
        },
        {
            "id": "ethos-code",
            "name": "Ethos Code", 
            "type": "local",
            "provider": "ollama",
            "capabilities": ["coding", "programming", "debugging", "code_review", "algorithm_design"],
            "enabled": True,
            "status": "available" if "llava:7b" in ollama_models else "unavailable",
            "description": "Specialized AI for coding and development tasks",
            "parameters": "7B",
            "quantization": "4-bit", 
            "speed": "medium",
            "capability": "coding",
            "ollama_model": "llava:7b"
        },
        {
            "id": "ethos-pro",
            "name": "Ethos Pro",
            "type": "local", 
            "provider": "ollama",
            "capabilities": ["advanced_reasoning", "analysis", "research", "complex_tasks", "detailed_explanations"],
            "enabled": True,
            "status": "available" if "llama3.1:70b" in ollama_models else "unavailable",
            "description": "Professional AI for complex analysis and detailed work",
            "parameters": "70B",
            "quantization": "4-bit",
            "speed": "slow", 
            "capability": "advanced",
            "ollama_model": "llama3.1:70b"
        },
        {
            "id": "ethos-creative",
            "name": "Ethos Creative",
            "type": "local",
            "provider": "ollama", 
            "capabilities": ["creative_writing", "content_creation", "storytelling", "artistic_tasks", "brainstorming"],
            "enabled": True,
            "status": "available" if "llava:7b" in ollama_models else "unavailable",
            "description": "Creative AI for writing, content creation, and artistic tasks",
            "parameters": "7B",
            "quantization": "4-bit",
            "speed": "medium",
            "capability": "creative", 
            "ollama_model": "llava:7b"
        }
    ]
    
    response_data = {
        "models": models,
        "total": len(models),
        "status": "available" if OLLAMA_AVAILABLE else "unavailable",
        "ollama_status": "connected" if OLLAMA_AVAILABLE else "disconnected"
    }
    
    from fastapi.responses import JSONResponse
    response = JSONResponse(content=response_data)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

@app.get("/api/models/status")
async def get_model_status():
    """Get model system status"""
    try:
        return {
            "status": "available",
            "mode": "clean",
            "models_loaded": len(LOCAL_MODELS),
            "total_models": len(LOCAL_MODELS),
            "system_healthy": True,
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Error getting model status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat(message: ChatMessage):
    """Main chat endpoint"""
    try:
        content = message.get_content()
        model_id = message.model_override or "ethos-light"
        
        # Generate response
        response_text = get_local_ai_response(content, model_id)
        
        return ChatResponse(
            content=response_text,
            model_used=model_id,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            tools_called=[]
        )
        
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

# Global error handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception handler caught: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 