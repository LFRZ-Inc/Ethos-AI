#!/usr/bin/env python3
"""
Simplified Ethos AI - FastAPI Application
Basic endpoints for frontend functionality
"""

import asyncio
import logging
import time
import json
from typing import Optional, List, Dict, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Ethos AI",
    description="Local-first hybrid AI interface",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ChatMessage(BaseModel):
    content: str
    conversation_id: Optional[str] = None
    model_override: Optional[str] = None
    use_tools: bool = True

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
config_data = {
    "api_keys": {
        "anthropic": "",
        "openai": "",
        "huggingface": ""
    },
    "tools": {
        "python_execution": True,
        "web_search": True,
        "file_search": True,
        "code_execution": True,
        "sandbox_mode": True
    },
    "memory": {
        "vector_store": "chromadb",
        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
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

# Mock models
MOCK_MODELS = {
    "llama3.2-3b": {
        "id": "llama3.2-3b",
        "name": "Llama 3.2 3B",
        "type": "local",
        "provider": "ollama",
        "capabilities": ["general_chat", "reasoning"],
        "enabled": True,
        "status": "available"
    },
    "codellama-7b": {
        "id": "codellama-7b",
        "name": "CodeLLaMA 7B",
        "type": "local",
        "provider": "ollama",
        "capabilities": ["coding", "programming"],
        "enabled": True,
        "status": "available"
    },
    "llava-7b": {
        "id": "llava-7b",
        "name": "LLaVA 7B",
        "type": "local",
        "provider": "ollama",
        "capabilities": ["image_analysis", "vision"],
        "enabled": True,
        "status": "available"
    }
}

@app.get("/")
async def root():
    return {"message": "Ethos AI Backend is running!"}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": time.time()}

@app.post("/api/chat")
async def chat(message: ChatMessage):
    try:
        # Mock AI response
        ai_response = f"I received your message: '{message.content}'. This is a mock response from the AI. In a real implementation, this would be processed by the selected model."
        
        # Create conversation if needed
        conv_id = message.conversation_id
        if not conv_id:
            global conversation_counter
            conversation_counter += 1
            conv_id = f"conv_{conversation_counter}"
            conversations[conv_id] = {
                "id": conv_id,
                "title": message.content[:50] + "..." if len(message.content) > 50 else message.content,
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "message_count": 0
            }
        
        # Store message
        if conv_id not in messages:
            messages[conv_id] = []
        
        messages[conv_id].append({
            "user": message.content,
            "assistant": ai_response,
            "model_used": message.model_override or "llama3.2-3b",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        })
        
        # Update conversation
        if conv_id in conversations:
            conversations[conv_id]["message_count"] = len(messages[conv_id])
            conversations[conv_id]["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        return ChatResponse(
            content=ai_response,
            model_used=message.model_override or "llama3.2-3b",
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            tools_called=[]
        )
        
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/models")
async def get_models():
    return {"models": list(MOCK_MODELS.values())}

@app.post("/api/conversations")
async def create_conversation(conversation: ConversationCreate):
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
    try:
        return {"conversations": list(conversations.values())}
    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
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
    try:
        # Mock file processing
        return {
            "filename": file.filename,
            "size": len(await file.read()),
            "analysis": {
                "summary": f"Mock analysis of {file.filename}",
                "type": "text",
                "content": f"This is a mock analysis of the uploaded file: {file.filename}"
            }
        }
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/config")
async def get_config():
    return {
        "models": MOCK_MODELS,
        "api_keys": config_data["api_keys"],
        "tools": config_data["tools"],
        "memory": config_data["memory"],
        "ui": config_data["ui"]
    }

@app.post("/api/config")
async def update_config(new_config: dict):
    try:
        global config_data
        # Update API keys if provided
        if "api_keys" in new_config:
            config_data["api_keys"].update(new_config["api_keys"])
        # Update other config sections if provided
        for key in ["tools", "memory", "ui"]:
            if key in new_config:
                config_data[key].update(new_config[key])
        
        return {"message": "Configuration updated successfully"}
    except Exception as e:
        logger.error(f"Error updating config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info") 