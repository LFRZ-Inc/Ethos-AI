#!/usr/bin/env python3
"""
Ethos AI - Main FastAPI Application
Local-first hybrid AI interface
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import our modules
from config.config import Config
from memory.database import Database
from memory.vector_store import VectorStore
from models.orchestrator import ModelOrchestrator
from tools.tool_manager import ToolManager
from utils.logger import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Global variables for components
config: Optional[Config] = None
orchestrator: Optional[ModelOrchestrator] = None
vector_store: Optional[VectorStore] = None
database: Optional[Database] = None
tool_manager: Optional[ToolManager] = None

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

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    global config, orchestrator, vector_store, database, tool_manager
    logger.info("Starting Ethos AI backend...")
    try:
        config = Config()
        database = Database(config.data_dir)
        await database.initialize()
        vector_store = VectorStore(config.data_dir)
        await vector_store.initialize()
        tool_manager = ToolManager(config, database, vector_store)
        await tool_manager.initialize()
        orchestrator = ModelOrchestrator(config, vector_store, tool_manager)
        await orchestrator.initialize()
        logger.info("Ethos AI backend started successfully")
    except Exception as e:
        logger.error(f"Failed to start backend: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Ethos AI backend...")
    if orchestrator:
        await orchestrator.cleanup()
    if vector_store:
        await vector_store.cleanup()
    if database:
        await database.cleanup()
    logger.info("Ethos AI backend shutdown complete")

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "Ethos AI Backend is running!",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "ethos-ai-backend",
        "models_available": len(config.get_enabled_models()) if config else 0
    }

# Chat endpoint
@app.post("/api/chat")
async def chat(message: ChatMessage):
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    try:
        response = await orchestrator.process_message(
            content=message.content,
            conversation_id=message.conversation_id,
            model_override=message.model_override,
            use_tools=message.use_tools
        )
        return ChatResponse(**response)
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Models endpoint
@app.get("/api/models")
async def get_models():
    if not config:
        raise HTTPException(status_code=503, detail="Config not initialized")
    
    models = []
    for model_id, model_config in config.get_enabled_models().items():
        models.append({
            "id": model_id,
            "name": model_config.name,
            "type": model_config.type,
            "provider": model_config.provider,
            "capabilities": model_config.capabilities,
            "enabled": model_config.enabled
        })
    
    return {"models": models}

# Conversations endpoints
@app.post("/api/conversations")
async def create_conversation(conversation: ConversationCreate):
    if not database:
        raise HTTPException(status_code=503, detail="Database not initialized")
    
    try:
        conv_id = await database.create_conversation(conversation.title)
        return ConversationResponse(
            conversation_id=conv_id,
            title=conversation.title,
            created_at=conv_id  # Simplified for now
        )
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/conversations")
async def get_conversations():
    if not database:
        raise HTTPException(status_code=503, detail="Database not initialized")
    
    try:
        conversations = await database.get_conversations()
        return {"conversations": conversations}
    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    if not database:
        raise HTTPException(status_code=503, detail="Database not initialized")
    
    try:
        conversation = await database.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return conversation
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    if not database:
        raise HTTPException(status_code=503, detail="Database not initialized")
    
    try:
        await database.delete_conversation(conversation_id)
        return {"message": "Conversation deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# File upload endpoint
@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    if not tool_manager:
        raise HTTPException(status_code=503, detail="Tool manager not initialized")
    
    try:
        result = await tool_manager.handle_file_upload(file)
        return result
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Memory search endpoint
@app.get("/api/memory/search")
async def search_memory(query: str, limit: int = 10):
    if not vector_store:
        raise HTTPException(status_code=503, detail="Vector store not initialized")
    
    try:
        results = await vector_store.search(query, limit=limit)
        return {"results": results}
    except Exception as e:
        logger.error(f"Error searching memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Tools endpoint
@app.post("/api/tools/{tool_name}")
async def execute_tool(tool_name: str, **kwargs):
    if not tool_manager:
        raise HTTPException(status_code=503, detail="Tool manager not initialized")
    
    try:
        result = await tool_manager.execute_tool(tool_name, **kwargs)
        return {"result": result}
    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Configuration endpoint
@app.get("/api/config")
async def get_config():
    if not config:
        raise HTTPException(status_code=503, detail="Config not initialized")
    
    return config.get_public_config()

@app.post("/api/config")
async def update_config(config_data: dict):
    if not config:
        raise HTTPException(status_code=503, detail="Config not initialized")
    
    try:
        config.update_config(config_data)
        return {"message": "Configuration updated successfully"}
    except Exception as e:
        logger.error(f"Error updating config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for real-time chat
@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Process the message and send response
            response = {"message": f"Echo: {data}"}
            await websocket.send_text(str(response))
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info") 