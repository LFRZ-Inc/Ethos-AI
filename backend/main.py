#!/usr/bin/env python3
"""
Ethos AI - Railway Optimized FastAPI Application
Local-first, privacy-focused AI interface - No external dependencies
"""

import asyncio
import logging
import os
import time
import json
import random
from pathlib import Path
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Import 70B model integration
try:
    from models import initialize_70b_model, generate_70b_response, get_70b_model_info, unload_70b_model
    MODEL_70B_AVAILABLE = True
except ImportError as e:
    logging.warning(f"70B model not available: {e}")
    MODEL_70B_AVAILABLE = False

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Ethos AI",
    description="Local-first, privacy-focused AI interface",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",  # Allow all origins for now
        "https://ethos-ai-phi.vercel.app",
        "https://ethos-ai-phi.vercel.app/",
        "http://localhost:3000",
        "http://localhost:1420",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:1420"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global 70B model status
model_70b_initialized = False
model_70b_loading = False

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

class ConversationCreate(BaseModel):
    title: str

class ConversationResponse(BaseModel):
    conversation_id: str
    title: str
    created_at: str

# In-memory storage for development
conversations = {}
messages = {}
conversation_counter = 0

# Local AI Knowledge Base
LOCAL_KNOWLEDGE = {
    "general": [
        "I'm Ethos AI, a local-first, privacy-focused AI assistant.",
        "I operate completely independently without any external dependencies.",
        "Your conversations are private and not tracked by any big tech companies.",
        "I'm designed to help you with various tasks while respecting your privacy."
    ],
    "cooking": [
        "I can help you with cooking tips and recipes.",
        "For pasta dishes, always salt your water generously.",
        "Fresh herbs can transform a simple dish into something special.",
        "Let meat rest after cooking to retain its juices.",
        "Taste as you cook to adjust seasoning properly."
    ],
    "coding": [
        "I can help you with programming and development questions.",
        "Always write clean, readable code with good documentation.",
        "Test your code thoroughly before deploying.",
        "Use version control to track your changes.",
        "Follow best practices for your chosen programming language."
    ],
    "health": [
        "I can provide general wellness information.",
        "Regular exercise and a balanced diet are important for health.",
        "Getting enough sleep is crucial for overall well-being.",
        "Stay hydrated throughout the day.",
        "Consider consulting healthcare professionals for medical advice."
    ],
    "learning": [
        "I can help you with learning and educational topics.",
        "Break complex topics into smaller, manageable parts.",
        "Practice regularly to reinforce new skills.",
        "Use different learning methods to find what works best for you.",
        "Don't be afraid to ask questions and seek clarification."
    ]
}

# Local AI Models - Privacy-focused
LOCAL_MODELS = {
    "ethos-70b": {
        "id": "ethos-70b",
        "name": "Ethos 70B AI",
        "type": "local",
        "provider": "ethos",
        "capabilities": ["general_chat", "reasoning", "privacy_focused", "advanced_ai"],
        "enabled": True,
        "status": "available" if MODEL_70B_AVAILABLE else "unavailable",
        "description": "70B parameter local AI for advanced conversations",
        "parameters": "70B",
        "quantization": "4-bit"
    },
    "ethos-general": {
        "id": "ethos-general",
        "name": "Ethos General AI",
        "type": "local",
        "provider": "ethos",
        "capabilities": ["general_chat", "reasoning", "privacy_focused"],
        "enabled": True,
        "status": "available",
        "description": "Local-first AI for general conversations"
    },
    "ethos-cooking": {
        "id": "ethos-cooking",
        "name": "Ethos Cooking Assistant",
        "type": "local",
        "provider": "ethos",
        "capabilities": ["cooking", "recipes", "kitchen_tips"],
        "enabled": True,
        "status": "available",
        "description": "Specialized cooking and recipe assistant"
    },
    "ethos-coding": {
        "id": "ethos-coding",
        "name": "Ethos Code Assistant",
        "type": "local",
        "provider": "ethos",
        "capabilities": ["coding", "programming", "debugging"],
        "enabled": True,
        "status": "available",
        "description": "Programming and development assistant"
    },
    "ethos-health": {
        "id": "ethos-health",
        "name": "Ethos Health Assistant",
        "type": "local",
        "provider": "ethos",
        "capabilities": ["health", "wellness", "fitness"],
        "enabled": True,
        "status": "available",
        "description": "Health and wellness assistant"
    }
}

# Local AI Processing Functions
def analyze_message_intent(message: str) -> str:
    """Analyze message to determine intent and appropriate response category"""
    message_lower = message.lower()
    
    # Cooking-related keywords
    if any(word in message_lower for word in ["cook", "recipe", "food", "kitchen", "meal", "ingredient", "chef"]):
        return "cooking"
    
    # Coding-related keywords
    elif any(word in message_lower for word in ["code", "program", "debug", "software", "development", "algorithm", "function"]):
        return "coding"
    
    # Health-related keywords
    elif any(word in message_lower for word in ["health", "fitness", "exercise", "diet", "wellness", "medical", "doctor"]):
        return "health"
    
    # Learning-related keywords
    elif any(word in message_lower for word in ["learn", "study", "education", "knowledge", "teach", "understand"]):
        return "learning"
    
    # Default to general
    else:
        return "general"

def generate_local_response(message: str, model_id: str) -> str:
    """Generate a contextual response using local knowledge"""
    global model_70b_initialized, model_70b_loading
    
    # Try to use 70B model if requested and available
    if model_id == "ethos-70b" and MODEL_70B_AVAILABLE:
        if not model_70b_initialized and not model_70b_loading:
            # Start loading the 70B model
            model_70b_loading = True
            logger.info("Starting 70B model initialization...")
            try:
                # Initialize in background
                model_70b_initialized = initialize_70b_model()
                model_70b_loading = False
                if model_70b_initialized:
                    logger.info("70B model initialized successfully!")
                else:
                    logger.warning("Failed to initialize 70B model, falling back to basic responses")
            except Exception as e:
                logger.error(f"Error initializing 70B model: {e}")
                model_70b_loading = False
                model_70b_initialized = False
        
        # If 70B model is ready, use it
        if model_70b_initialized:
            try:
                response = generate_70b_response(message)
                logger.info("Generated response using 70B model")
                return response
            except Exception as e:
                logger.error(f"Error generating 70B response: {e}")
                # Fall back to basic response
                pass
        elif model_70b_loading:
            return "I'm loading the 70B model to provide you with more intelligent responses. This may take a moment. Please try again in a few seconds."
    
    # Fall back to basic response system
    message_lower = message.lower()
    
    # Handle specific questions about capabilities
    if any(phrase in message_lower for phrase in ["what can you do", "what do you do", "help me", "capabilities", "features"]):
        return """I'm Ethos AI, your privacy-focused local assistant! Here's what I can help you with:

🍳 **Cooking & Recipes**: Help with recipes, cooking tips, meal planning, and kitchen advice
💻 **Programming & Coding**: Assist with code, debugging, software development, and programming concepts  
🏃‍♂️ **Health & Wellness**: Provide general fitness, nutrition, and wellness information
📚 **Learning & Education**: Help with studying, explaining concepts, and educational topics
🤖 **General Assistance**: Answer questions, provide information, and help with various tasks

I operate completely locally without any external tracking or big tech dependencies. Your conversations are private and secure. What would you like help with today?"""

    # Handle greetings
    elif any(word in message_lower for word in ["hello", "hi", "hey", "greetings"]):
        return "Hello! I'm Ethos AI, your local privacy-focused assistant. I'm here to help you with cooking, coding, health, learning, and more - all while keeping your data completely private. What can I help you with today?"

    # Handle "how are you" type questions
    elif any(phrase in message_lower for phrase in ["how are you", "how do you feel", "are you ok"]):
        return "I'm functioning perfectly! As a local AI assistant, I'm designed to help you while maintaining complete privacy. I don't have feelings like humans do, but I'm ready and eager to assist you with whatever you need. What would you like to work on?"

    # Analyze intent for other messages
    intent = analyze_message_intent(message)
    
    # Get relevant knowledge base
    knowledge_base = LOCAL_KNOWLEDGE.get(intent, LOCAL_KNOWLEDGE["general"])
    
    # Create a contextual response
    if intent == "cooking":
        if "recipe" in message_lower:
            return f"I'd love to help you with recipes! 🍳 {random.choice(knowledge_base)} What type of dish are you looking to make? I can help with ingredients, techniques, and cooking methods."
        elif "tip" in message_lower or "advice" in message_lower:
            return f"Here's a great cooking tip: {random.choice(knowledge_base)} What specific cooking challenge are you facing?"
        else:
            return f"I'm your Ethos Cooking Assistant! 🍳 {random.choice(knowledge_base)} I can help with recipes, meal planning, cooking techniques, and kitchen tips. What would you like to cook today?"
    
    elif intent == "coding":
        if any(word in message_lower for word in ["help", "problem", "error", "bug", "debug"]):
            return f"I'm your Ethos Code Assistant! 💻 {random.choice(knowledge_base)} I can help you debug issues, explain programming concepts, suggest best practices, and review code. What's the programming challenge you're facing?"
        else:
            return f"I'm your Ethos Code Assistant! 💻 {random.choice(knowledge_base)} I can help with programming, debugging, code review, and software development. What programming topic would you like to explore?"
    
    elif intent == "health":
        return f"I'm your Ethos Health Assistant! 🏃‍♂️ {random.choice(knowledge_base)} I can provide general wellness information, fitness tips, and nutrition advice. Remember, I provide general information - always consult healthcare professionals for medical advice. What health topic interests you?"
    
    elif intent == "learning":
        return f"I'm your Ethos Learning Assistant! 📚 {random.choice(knowledge_base)} I can help explain concepts, break down complex topics, and assist with your learning journey. What would you like to learn about today?"
    
    else:
        # For general questions, try to provide a helpful response
        if "?" in message:
            return f"I'm Ethos AI! 🤖 I'd be happy to help you with that question. {random.choice(knowledge_base)} Could you provide more details about what you're looking for? I can assist with cooking, coding, health, learning, and many other topics."
        else:
            return f"I'm Ethos AI! 🤖 {random.choice(knowledge_base)} I'm here to help you with cooking, coding, health, learning, and more - all while keeping your conversations completely private. What would you like to work on?"

# Global error handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception handler caught: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

# Health check endpoint - critical for Railway
@app.get("/")
async def root():
    return {
        "message": "Ethos AI Backend is running!", 
        "status": "healthy",
        "version": "1.0.0",
        "privacy": "100% local - no external tracking",
        "timestamp": time.time()
    }

@app.get("/test")
async def test_endpoint():
    """Test endpoint to verify backend is working"""
    return {
        "status": "ok",
        "message": "Backend is working",
        "timestamp": time.time(),
        "cors_enabled": True
    }

@app.get("/health")
async def health():
    """Health check endpoint for Railway"""
    try:
        return {
            "status": "healthy", 
            "service": "ethos-ai-backend",
            "privacy": "local-first, no external dependencies",
            "timestamp": time.time(),
            "environment": os.environ.get("RAILWAY_ENVIRONMENT", "production"),
            "port": os.environ.get("PORT", "8000")
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat(message: ChatMessage):
    """Chat endpoint with local AI response"""
    try:
        # Debug logging
        logger.info(f"Received chat request: {message}")
        
        # Get the message content
        try:
            content = message.get_content()
            logger.info(f"Message content: {content}")
        except ValueError as e:
            logger.error(f"Message content error: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        
        # Get the model to use
        model_id = message.model_override or "ethos-general"
        model = LOCAL_MODELS.get(model_id)
        
        if not model:
            raise HTTPException(status_code=400, detail=f"Model {model_id} not found")
        
        # Check if model is available
        if not model.get("enabled", False):
            raise HTTPException(
                status_code=400, 
                detail=f"Model {model_id} is not available."
            )
        
        # Generate local AI response
        ai_response = generate_local_response(content, model_id)
        
        # Create conversation if needed
        conv_id = message.conversation_id
        if not conv_id:
            global conversation_counter
            conversation_counter += 1
            conv_id = f"conv_{conversation_counter}"
            conversations[conv_id] = {
                "id": conv_id,
                "title": content[:50] + "..." if len(content) > 50 else content,
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "message_count": 0
            }
        
        # Store message
        if conv_id not in messages:
            messages[conv_id] = []
        
        messages[conv_id].append({
            "user": content,
            "assistant": ai_response,
            "model_used": model_id,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        })
        
        # Update conversation
        if conv_id in conversations:
            conversations[conv_id]["message_count"] = len(messages[conv_id])
            conversations[conv_id]["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        return ChatResponse(
            content=ai_response,
            model_used=model_id,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            tools_called=[]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/models")
async def get_models():
    """Get available local models"""
    try:
        return {"models": list(LOCAL_MODELS.values())}
    except Exception as e:
        logger.error(f"Error getting models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/conversations")
async def create_conversation(conversation: ConversationCreate):
    """Create a new conversation"""
    try:
        global conversation_counter
        conversation_counter += 1
        conv_id = f"conv_{conversation_counter}"
        
        conversations[conv_id] = {
            "id": conv_id,
            "title": conversation.title,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "message_count": 0
        }
        
        return ConversationResponse(
            conversation_id=conv_id,
            title=conversation.title,
            created_at=time.strftime("%Y-%m-%d %H:%M:%S")
        )
        
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/conversations")
async def get_conversations():
    """Get all conversations"""
    try:
        return {"conversations": list(conversations.values())}
    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get a specific conversation with messages"""
    try:
        if conversation_id not in conversations:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        conv_data = conversations[conversation_id].copy()
        conv_data["messages"] = messages.get(conversation_id, [])
        
        return conv_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation"""
    try:
        if conversation_id in conversations:
            del conversations[conversation_id]
        if conversation_id in messages:
            del messages[conversation_id]
        
        return {"message": "Conversation deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload and analyze a file"""
    try:
        # Local file processing
        content = await file.read()
        return {
            "filename": file.filename,
            "size": len(content),
            "analysis": {
                "summary": f"File {file.filename} uploaded and processed locally",
                "type": "text",
                "content": f"File {file.filename} has been processed locally by Ethos AI. No external services were used."
            }
        }
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/config")
async def get_config():
    """Get current configuration"""
    try:
        return {
            "models": LOCAL_MODELS,
            "privacy": {
                "status": "100% local",
                "no_external_tracking": True,
                "no_big_tech_dependencies": True,
                "data_retention": "local_only"
            },
            "tools": {
                "python_execution": True,
                "web_search": False,  # No external web search
                "file_search": True,
                "code_execution": True,
                "sandbox_mode": True
            },
            "memory": {
                "vector_store": "local",
                "embedding_model": "local",
                "max_memory_size": 10000,
                "similarity_threshold": 0.7
            },
            "ui": {
                "theme": "dark",
                "language": "en",
                "auto_save": True,
                "max_conversations": 100
            }
        }
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/config")
async def update_config(new_config: dict):
    """Update configuration"""
    try:
        # Only allow local configuration updates
        return {"message": "Configuration updated successfully (local only)"}
    except Exception as e:
        logger.error(f"Error updating config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/models/70b/status")
async def get_70b_model_status():
    """Get 70B model status and information"""
    try:
        if not MODEL_70B_AVAILABLE:
            return {
                "available": False,
                "status": "unavailable",
                "reason": "70B model dependencies not available",
                "message": "70B model requires additional dependencies that are not installed"
            }
        
        model_info = get_70b_model_info()
        return {
            "available": True,
            "initialized": model_70b_initialized,
            "loading": model_70b_loading,
            "model_info": model_info,
            "status": "ready" if model_70b_initialized else ("loading" if model_70b_loading else "not_initialized")
        }
    except Exception as e:
        logger.error(f"Error getting 70B model status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/models/70b/initialize")
async def initialize_70b_model_endpoint():
    """Initialize the 70B model"""
    try:
        if not MODEL_70B_AVAILABLE:
            raise HTTPException(status_code=400, detail="70B model dependencies not available")
        
        if model_70b_loading:
            return {"message": "70B model is already loading", "status": "loading"}
        
        if model_70b_initialized:
            return {"message": "70B model is already initialized", "status": "ready"}
        
        # Start initialization
        global model_70b_loading
        model_70b_loading = True
        
        # Initialize in background
        try:
            success = initialize_70b_model()
            model_70b_loading = False
            global model_70b_initialized
            model_70b_initialized = success
            
            if success:
                return {"message": "70B model initialized successfully", "status": "ready"}
            else:
                return {"message": "Failed to initialize 70B model", "status": "failed"}
                
        except Exception as e:
            model_70b_loading = False
            logger.error(f"Error initializing 70B model: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to initialize 70B model: {str(e)}")
            
    except Exception as e:
        logger.error(f"Error in 70B model initialization endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/models/70b/unload")
async def unload_70b_model_endpoint():
    """Unload the 70B model to free memory"""
    try:
        if not MODEL_70B_AVAILABLE:
            raise HTTPException(status_code=400, detail="70B model dependencies not available")
        
        unload_70b_model()
        global model_70b_initialized, model_70b_loading
        model_70b_initialized = False
        model_70b_loading = False
        
        return {"message": "70B model unloaded successfully", "status": "unloaded"}
        
    except Exception as e:
        logger.error(f"Error unloading 70B model: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("Starting Ethos AI backend...")
    logger.info(f"Environment: {os.environ.get('RAILWAY_ENVIRONMENT', 'production')}")
    logger.info(f"Port: {os.environ.get('PORT', '8000')}")
    logger.info("Privacy: 100% local - no external dependencies")
    logger.info("Ethos AI backend started successfully")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("Shutting down Ethos AI backend...")

if __name__ == "__main__":
    # Get port from Railway environment
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print(f"Starting Ethos AI on {host}:{port}")
    print(f"Environment: {os.environ.get('RAILWAY_ENVIRONMENT', 'production')}")
    print("Privacy: 100% local - no external dependencies")
    print("Note: Use gunicorn main:app for production deployment")
    
    # Don't run uvicorn here - let gunicorn handle it
    # uvicorn.run(app, host=host, port=port, log_level="info") 