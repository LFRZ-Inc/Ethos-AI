#!/usr/bin/env python3
"""
Ethos AI - Clean Railway Backend
No heavy dependencies, guaranteed to work
"""

import os
import logging
import time
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
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
    description="Clean AI backend for Railway deployment",
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

# Simple AI Models - No heavy dependencies
LOCAL_MODELS = {
    "ethos-light": {
        "id": "ethos-light",
        "name": "Ethos Light",
        "type": "local",
        "provider": "ethos",
        "capabilities": ["general_chat", "privacy_focused", "basic_assistance", "fast_responses"],
        "enabled": True,
        "status": "available",
        "description": "Lightweight AI for quick responses and basic tasks",
        "parameters": "lightweight",
        "quantization": "none",
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
        "status": "available",
        "description": "Specialized AI for coding and development tasks",
        "parameters": "code-focused",
        "quantization": "none",
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
        "status": "available",
        "description": "Professional AI for complex analysis and detailed work",
        "parameters": "advanced",
        "quantization": "none",
        "speed": "medium",
        "capability": "advanced"
    },
    "ethos-creative": {
        "id": "ethos-creative",
        "name": "Ethos Creative",
        "type": "local",
        "provider": "ethos",
        "capabilities": ["creative_writing", "content_creation", "storytelling", "artistic_tasks", "brainstorming"],
        "enabled": True,
        "status": "available",
        "description": "Creative AI for writing, content creation, and artistic tasks",
        "parameters": "creative",
        "quantization": "none",
        "speed": "medium",
        "capability": "creative"
    }
}

def generate_simple_response(message: str, model_id: str = "ethos-light") -> str:
    """Generate simple responses based on model type"""
    message_lower = message.lower()
    
    # Handle greetings
    if any(word in message_lower for word in ["hello", "hi", "hey", "greetings"]):
        return "Hello! I'm Ethos AI, your privacy-focused assistant. I'm currently running in clean mode and can help you with various tasks. What can I assist you with today?"
    
    # Handle capability questions
    if any(phrase in message_lower for phrase in ["what can you do", "what do you do", "help me", "capabilities", "features"]):
        return """I'm Ethos AI, your privacy-focused assistant! Here's what I can help you with:

🤖 **Current Mode**: Clean AI (lightweight deployment)
💬 **General Chat**: I can engage in conversations and answer questions
📝 **Text Processing**: Help with writing, editing, and text analysis
🧮 **Basic Reasoning**: Simple problem-solving and explanations
🔒 **Privacy**: 100% local processing - no external tracking

I'm running in clean mode for reliable Railway deployment. What would you like help with?"""
    
    # Model-specific responses
    if model_id == "ethos-code":
        if any(word in message_lower for word in ["code", "program", "debug", "algorithm", "function", "python", "javascript", "html", "css"]):
            return f"I'm Ethos Code, specialized for programming tasks! I can help you with {message}. I can assist with code writing, debugging, algorithm design, and code review. What specific coding question do you have?"
        else:
            return f"I'm Ethos Code, your coding assistant! While I'm specialized for programming tasks, I can also help with general questions. For coding help, just ask about programming, debugging, or any programming language!"
    
    elif model_id == "ethos-pro":
        if "?" in message:
            return f"I'm Ethos Pro, designed for detailed analysis and complex reasoning! I can provide in-depth analysis of {message}. I'm particularly good at research, analysis, and detailed explanations. What aspect would you like me to explore?"
        else:
            return f"I'm Ethos Pro, your professional analysis assistant! I can help with complex reasoning, detailed analysis, research tasks, and comprehensive explanations. What would you like me to analyze?"
    
    elif model_id == "ethos-creative":
        if any(word in message_lower for word in ["write", "story", "creative", "content", "art", "design", "poem", "article"]):
            return f"I'm Ethos Creative, your creative writing assistant! I can help you with {message}. I'm specialized for storytelling, content creation, creative writing, and artistic tasks. What would you like to create?"
        else:
            return f"I'm Ethos Creative, designed for creative tasks! I can help with writing, storytelling, content creation, brainstorming, and artistic projects. What creative project would you like to work on?"
    
    else:  # ethos-light (default)
        if any(word in message_lower for word in ["code", "program", "debug", "algorithm", "function", "python", "javascript"]):
            return f"I can help you with programming questions! I'm currently in clean mode, but I can still provide basic coding assistance, explain concepts, and help with simple programming problems. What specific coding question do you have about {message}?"
        elif "?" in message:
            return f"That's an interesting question about {message}! I'm currently running in clean mode for reliable deployment. I can provide basic information and help with various topics. What specific aspect would you like me to help with?"
        else:
            return f"I understand you're asking about {message}. I'm currently running in clean mode for reliable deployment. I can provide basic assistance and engage in conversation. How can I help you with this topic?"

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
    try:
        response_data = {
            "models": list(LOCAL_MODELS.values()),
            "total": len(LOCAL_MODELS),
            "status": "available"
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
        response_text = generate_simple_response(content, model_id)
        
        return ChatResponse(
            content=response_text,
            model_used=model_id,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            tools_called=[]
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/conversations")
async def get_conversations():
    """Get all conversations"""
    try:
        return {
            "conversations": list(conversations.values()),
            "total": len(conversations)
        }
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