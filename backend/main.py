#!/usr/bin/env python3
"""
Ethos AI - Main FastAPI Application
Local-first hybrid AI interface with multi-model orchestration
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent))

from config.config import Config
from models.orchestrator import ModelOrchestrator
from memory.vector_store import VectorStore
from memory.database import Database
from tools.tool_manager import ToolManager
from utils.logger import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Ethos AI",
    description="Local-first hybrid AI interface",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
config: Optional[Config] = None
orchestrator: Optional[ModelOrchestrator] = None
vector_store: Optional[VectorStore] = None
database: Optional[Database] = None
tool_manager: Optional[ToolManager] = None

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# Pydantic models
class ChatMessage(BaseModel):
    content: str
    conversation_id: Optional[str] = None
    model_override: Optional[str] = None
    use_tools: bool = True

class ChatResponse(BaseModel):
    content: str
    model_used: str
    conversation_id: str
    timestamp: str
    tools_called: List[Dict] = []

class Conversation(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str
    message_count: int

class ModelInfo(BaseModel):
    id: str
    name: str
    type: str  # local, cloud
    status: str  # available, unavailable, loading
    capabilities: List[str]

@app.on_event("startup")
async def startup_event():
    """Initialize all components on startup"""
    global config, orchestrator, vector_store, database, tool_manager
    
    logger.info("Starting Ethos AI backend...")
    
    try:
        # Load configuration
        config = Config()
        logger.info("Configuration loaded successfully")
        
        # Initialize database
        database = Database(config.data_dir)
        await database.initialize()
        logger.info("Database initialized")
        
        # Initialize vector store
        vector_store = VectorStore(config.data_dir)
        await vector_store.initialize()
        logger.info("Vector store initialized")
        
        # Initialize tool manager
        tool_manager = ToolManager(config, database, vector_store)
        await tool_manager.initialize()
        logger.info("Tool manager initialized")
        
        # Initialize model orchestrator
        orchestrator = ModelOrchestrator(config, vector_store, tool_manager)
        await orchestrator.initialize()
        logger.info("Model orchestrator initialized")
        
        logger.info("Ethos AI backend started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start backend: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Ethos AI backend...")
    
    if orchestrator:
        await orchestrator.cleanup()
    
    if vector_store:
        await vector_store.cleanup()
    
    if database:
        await database.cleanup()
    
    logger.info("Backend shutdown complete")

# API Endpoints

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Ethos AI",
        "version": "1.0.0"
    }

@app.get("/api/models")
async def get_models() -> List[ModelInfo]:
    """Get available models"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    models = await orchestrator.get_available_models()
    return [ModelInfo(**model) for model in models]

@app.get("/api/conversations")
async def get_conversations() -> List[Conversation]:
    """Get all conversations"""
    if not database:
        raise HTTPException(status_code=503, detail="Database not initialized")
    
    conversations = await database.get_conversations()
    return [Conversation(**conv) for conv in conversations]

@app.get("/api/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get specific conversation"""
    if not database:
        raise HTTPException(status_code=503, detail="Database not initialized")
    
    conversation = await database.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return conversation

@app.post("/api/chat")
async def chat(message: ChatMessage):
    """Process chat message"""
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

@app.post("/api/conversations")
async def create_conversation(title: str = "New Conversation"):
    """Create new conversation"""
    if not database:
        raise HTTPException(status_code=503, detail="Database not initialized")
    
    conversation_id = await database.create_conversation(title)
    return {"conversation_id": conversation_id}

@app.delete("/api/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete conversation"""
    if not database:
        raise HTTPException(status_code=503, detail="Database not initialized")
    
    success = await database.delete_conversation(conversation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {"status": "deleted"}

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload file for analysis"""
    if not tool_manager:
        raise HTTPException(status_code=503, detail="Tool manager not initialized")
    
    try:
        result = await tool_manager.process_file_upload(file)
        return result
    except Exception as e:
        logger.error(f"Error processing file upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/memory/search")
async def search_memory(query: str, limit: int = 10):
    """Search conversation memory"""
    if not vector_store:
        raise HTTPException(status_code=503, detail="Vector store not initialized")
    
    try:
        results = await vector_store.search(query, limit)
        return {"results": results}
    except Exception as e:
        logger.error(f"Error searching memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tools")
async def get_available_tools():
    """Get available tools"""
    if not tool_manager:
        raise HTTPException(status_code=503, detail="Tool manager not initialized")
    
    tools = await tool_manager.get_available_tools()
    return {"tools": tools}

# WebSocket endpoint for real-time chat
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            
            # Process the message
            if not orchestrator:
                await manager.send_personal_message(
                    '{"error": "Orchestrator not initialized"}', 
                    websocket
                )
                continue
            
            try:
                # Parse the message (assuming JSON format)
                import json
                message_data = json.loads(data)
                
                response = await orchestrator.process_message(
                    content=message_data.get("content", ""),
                    conversation_id=message_data.get("conversation_id"),
                    model_override=message_data.get("model_override"),
                    use_tools=message_data.get("use_tools", True)
                )
                
                await manager.send_personal_message(
                    json.dumps(response), 
                    websocket
                )
                
            except Exception as e:
                error_response = {"error": str(e)}
                await manager.send_personal_message(
                    json.dumps(error_response), 
                    websocket
                )
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Configuration endpoints
@app.get("/api/config")
async def get_config():
    """Get current configuration"""
    if not config:
        raise HTTPException(status_code=503, detail="Configuration not loaded")
    
    return config.get_public_config()

@app.post("/api/config")
async def update_config(config_data: Dict):
    """Update configuration"""
    if not config:
        raise HTTPException(status_code=503, detail="Configuration not loaded")
    
    try:
        config.update_config(config_data)
        return {"status": "updated"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    ) 