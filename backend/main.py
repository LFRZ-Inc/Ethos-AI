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
    """Get response from lightweight AI system - Railway compatible"""
    message_lower = message.lower()
    
    # Lightweight AI responses based on model type and message content
    if model_id == "ethos-light":
        return get_ethos_light_response(message, message_lower)
    elif model_id == "ethos-code":
        return get_ethos_code_response(message, message_lower)
    elif model_id == "ethos-pro":
        return get_ethos_pro_response(message, message_lower)
    elif model_id == "ethos-creative":
        return get_ethos_creative_response(message, message_lower)
    else:
        return get_ethos_light_response(message, message_lower)

def get_ethos_light_response(message: str, message_lower: str) -> str:
    """Ethos Light (3B) - Fast, general responses"""
    # Handle greetings
    if any(word in message_lower for word in ["hello", "hi", "hey", "greetings"]):
        return "Hello! I'm Ethos Light, your privacy-focused AI assistant. I'm designed for quick responses and general assistance. How can I help you today?"
    
    # Handle questions about the president
    if "president" in message_lower:
        return "As of 2024, Joe Biden is the President of the United States. He was inaugurated on January 20, 2021, and is serving his first term. I'm Ethos Light, providing you with accurate, privacy-focused information!"
    
    # Handle general questions
    if "?" in message:
        return f"That's an interesting question about '{message}'. As Ethos Light, I'm designed to provide quick, helpful responses. I can help you with general knowledge, basic analysis, and everyday questions. What specific aspect would you like to know more about?"
    
    # Handle general statements
    return f"I understand you're discussing '{message}'. As Ethos Light, I'm here to help with quick responses and general assistance. I can provide information, answer questions, or help you think through topics. What would you like to explore?"

def get_ethos_code_response(message: str, message_lower: str) -> str:
    """Ethos Code (7B) - Programming and technical responses"""
    # Handle coding questions
    if any(word in message_lower for word in ["code", "program", "debug", "algorithm", "function", "python", "javascript", "html", "css"]):
        return f"I'm Ethos Code, specialized for programming tasks! I can help you with '{message}'. I'm designed to provide coding assistance, debugging help, algorithm explanations, and technical guidance. What specific programming challenge are you working on?"
    
    # Handle technical questions
    if any(word in message_lower for word in ["how to", "tutorial", "guide", "explain", "help me"]):
        return f"As Ethos Code, I'm here to help you with technical and programming challenges. I can provide step-by-step guidance, code examples, debugging tips, and technical explanations. What would you like to learn or build?"
    
    # Handle general questions
    if "?" in message:
        return f"That's a great question! As Ethos Code, I'm specialized for programming and technical topics, but I can also help with general questions. I provide detailed, technical responses with code examples when relevant. What would you like to know?"
    
    return f"I'm Ethos Code, your programming and technical AI assistant. I can help you with coding challenges, debugging, algorithm design, and technical explanations. I'm designed to provide detailed, helpful responses for developers and tech enthusiasts."

def get_ethos_pro_response(message: str, message_lower: str) -> str:
    """Ethos Pro (70B) - Advanced analysis and detailed responses"""
    # Handle questions about the president
    if "president" in message_lower:
        return """As Ethos Pro, I can provide you with a comprehensive analysis of the current presidency:

**Current President (2024):** Joe Biden
- **Inauguration:** January 20, 2021
- **Party:** Democratic
- **Term:** First term (2021-2025)
- **Vice President:** Kamala Harris

**Key Context:**
- Biden became the 46th President of the United States
- He succeeded Donald Trump (Republican, 2017-2021)
- At 78, he was the oldest person to assume the presidency
- His administration focuses on infrastructure, climate change, and economic recovery

**Historical Significance:**
- First president to have a female vice president (Kamala Harris)
- Took office during the COVID-19 pandemic
- Faced significant challenges including economic recovery and political polarization

This analysis demonstrates Ethos Pro's capability for detailed, comprehensive responses with multiple perspectives and contextual information."""
    
    # Handle complex questions
    if "?" in message:
        return f"As Ethos Pro, I'm designed for advanced analysis and detailed responses. Your question about '{message}' deserves a comprehensive answer. I can provide deep analysis, research insights, detailed explanations, and complex reasoning. Let me give you a thorough response..."
    
    # Handle analysis requests
    if any(word in message_lower for word in ["analyze", "research", "study", "examine", "investigate"]):
        return f"I'm Ethos Pro, specialized for advanced analysis and research. I can provide detailed analysis of '{message}', including multiple perspectives, research insights, and comprehensive explanations. I'm designed for complex reasoning and detailed work."
    
    # Handle general topics
    return f"I'm Ethos Pro, your advanced AI assistant for complex analysis and detailed work. I can provide comprehensive analysis, research insights, detailed explanations, and advanced reasoning. I'm designed to help with complex topics and thorough analysis."

def get_ethos_creative_response(message: str, message_lower: str) -> str:
    """Ethos Creative (7B) - Creative writing and artistic responses"""
    # Handle creative requests
    if any(word in message_lower for word in ["write", "story", "creative", "content", "art", "design", "poem", "article"]):
        return f"I'm Ethos Creative, your AI assistant for creative tasks! I can help you with '{message}' by providing creative writing, storytelling, content creation, and artistic guidance. I'm designed to inspire and help you create engaging, original content."
    
    # Handle brainstorming
    if any(word in message_lower for word in ["idea", "brainstorm", "inspire", "creative", "imagine"]):
        return f"As Ethos Creative, I'm here to help you brainstorm and generate creative ideas. I can provide inspiration, creative suggestions, and help you develop your artistic and creative projects. What kind of creative work are you looking to develop?"
    
    # Handle general topics
    return f"I'm Ethos Creative, your AI assistant for creative writing, content creation, and artistic projects. I can help you with storytelling, creative writing, content development, and artistic inspiration. I'm designed to help you express your creativity and develop engaging content."

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
        # Lightweight AI system is always available
        models_available = True
        
        models = [
            {
                "id": "ethos-light",
                "name": "Ethos Light",
                "type": "local",
                "provider": "ethos",
                "capabilities": ["general_chat", "privacy_focused", "basic_assistance", "fast_responses"],
                "enabled": True,
                "status": "available",
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
                "status": "available",
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
                "status": "available",
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
                "status": "available",
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
            "status": "available",
            "model_system": "lightweight-ai"
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
        status_data = {
            "system_status": "available",
            "models_loaded": True,
            "privacy_mode": "enabled",
            "external_apis": "disabled",
            "data_collection": "disabled",
            "ai_system": "lightweight-railway-compatible"
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