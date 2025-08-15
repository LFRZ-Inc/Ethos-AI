#!/usr/bin/env python3
"""
Ethos AI - Simplified Railway Backend
Basic API endpoints without heavy AI dependencies
"""

import os
import logging
import time
import json
from typing import Optional, Dict, Any, List
from pathlib import Path

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
    description="Simplified AI backend for Railway deployment",
    version="1.0.0"
)

# Add CORS middleware with explicit configuration
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

# Simplified AI Models - No heavy dependencies
LOCAL_MODELS = {
    "ethos-fallback": {
        "id": "ethos-fallback",
        "name": "Ethos Fallback AI",
        "type": "local",
        "provider": "ethos",
        "capabilities": ["general_chat", "privacy_focused", "basic_assistance"],
        "enabled": True,
        "status": "available",
        "description": "Fallback AI system for basic assistance",
        "parameters": "fallback",
        "quantization": "none",
        "speed": "fast",
        "capability": "basic"
    },
    "ethos-simple": {
        "id": "ethos-simple",
        "name": "Ethos Simple AI",
        "type": "local",
        "provider": "ethos",
        "capabilities": ["general_chat", "basic_reasoning", "privacy_focused"],
        "enabled": True,
        "status": "available",
        "description": "Simple AI for basic conversations",
        "parameters": "simple",
        "quantization": "none",
        "speed": "fast",
        "capability": "basic"
    }
}

def generate_simple_response(message: str, model_id: str = "ethos-fallback") -> str:
    """Generate simple responses without heavy AI dependencies"""
    message_lower = message.lower()
    
    # Handle greetings
    if any(word in message_lower for word in ["hello", "hi", "hey", "greetings"]):
        return "Hello! I'm Ethos AI, your privacy-focused assistant. I'm currently running in simplified mode and can help you with basic tasks and questions. What can I assist you with today?"
    
    # Handle capability questions
    if any(phrase in message_lower for phrase in ["what can you do", "what do you do", "help me", "capabilities", "features"]):
        return """I'm Ethos AI, your privacy-focused assistant! Here's what I can help you with:

🤖 **Current Mode**: Simplified AI (lightweight deployment)
💬 **General Chat**: I can engage in conversations and answer questions
📝 **Text Processing**: Help with writing, editing, and text analysis
🧮 **Basic Reasoning**: Simple problem-solving and explanations
🔒 **Privacy**: 100% local processing - no external tracking

I'm running in simplified mode for Railway deployment. What would you like help with?"""
    
    # Handle questions about the system
    if any(phrase in message_lower for phrase in ["why simplified", "simplified mode", "system status", "what's wrong"]):
        return "I'm running in simplified mode to ensure reliable deployment on Railway. This version focuses on basic functionality without heavy AI model dependencies. I can still help you with various tasks!"
    
    # Handle coding questions
    if any(word in message_lower for word in ["code", "program", "debug", "algorithm", "function", "python", "javascript"]):
        return f"I can help you with programming questions! I'm currently in simplified mode, but I can still provide basic coding assistance, explain concepts, and help with simple programming problems. What specific coding question do you have about {message}?"
    
    # Handle general questions
    if "?" in message:
        return f"That's an interesting question about {message}! I'm currently running in simplified mode for reliable deployment. I can provide basic information and help with various topics. What specific aspect would you like me to help with?"
    
    # Handle statements
    if any(word in message_lower for word in ["thanks", "thank you", "appreciate"]):
        return "You're welcome! I'm happy to help. I'm running in simplified mode for reliable deployment, but I can still assist you with various tasks. Is there anything else you'd like help with?"
    
    # Default response
    return f"I understand you're asking about {message}. I'm currently running in simplified mode for reliable deployment. I can provide basic assistance and engage in conversation. How can I help you with this topic?"

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Ethos AI Backend is running!", 
        "status": "healthy",
        "version": "1.0.0",
        "mode": "simplified",
        "privacy": "100% local - no external tracking",
        "timestamp": time.time()
    }

@app.get("/health")
async def health():
    """Health check endpoint for Railway"""
    try:
        return {
            "status": "healthy", 
            "service": "ethos-ai-backend",
            "mode": "simplified",
            "privacy": "local-first, no external dependencies",
            "timestamp": time.time(),
            "environment": os.environ.get("RAILWAY_ENVIRONMENT", "production"),
            "port": os.environ.get("PORT", "8000")
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test")
async def test_endpoint():
    """Test endpoint to verify backend is working"""
    return {
        "status": "ok",
        "message": "Backend is working",
        "mode": "simplified",
        "timestamp": time.time(),
        "cors_enabled": True
    }

@app.get("/api/models")
async def get_models():
    """Get available models"""
    try:
        return {
            "models": list(LOCAL_MODELS.values()),
            "total": len(LOCAL_MODELS),
            "status": "available"
        }
    except Exception as e:
        logger.error(f"Error getting models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/models/status")
async def get_model_status():
    """Get model system status"""
    try:
        return {
            "status": "available",
            "mode": "simplified",
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
        model_id = message.model_override or "ethos-fallback"
        
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
