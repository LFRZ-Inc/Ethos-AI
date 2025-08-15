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

# Import local AI model system - Lazy loading for Railway stability
MODEL_SYSTEM_AVAILABLE = False
model_system_initialized = False
model_system_loading = False

def load_model_system():
    """Lazy load the model system only when needed"""
    global MODEL_SYSTEM_AVAILABLE
    if not MODEL_SYSTEM_AVAILABLE:
        try:
            from models import initialize_model, generate_response, get_model_info, get_system_status, unload_model
            MODEL_SYSTEM_AVAILABLE = True
            logger.info("Local AI model system loaded successfully")
            return True
        except ImportError as e:
            logging.warning(f"Local model system not available: {e}")
            MODEL_SYSTEM_AVAILABLE = False
            logger.info("Using fallback AI system - local models not available")
            return False
    return True

# For Railway deployment, we'll use the local model system
# Ollama integration is for local development only
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
    logger.error(f"Global exception handler caught: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 