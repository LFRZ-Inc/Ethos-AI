#!/usr/bin/env python3
"""
Ethos AI - Main FastAPI Application
Local-first hybrid AI interface
"""

import asyncio
import logging
import os
import time
from pathlib import Path
from typing import Optional, Dict, Any

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Load environment variables
from dotenv import load_dotenv
try:
    load_dotenv()
except Exception as e:
    print(f"Warning: Could not load .env file: {e}")

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
        
        # Initialize vector store
        try:
            vector_store = VectorStore(config.data_dir)
            await vector_store.initialize()
            logger.info("Vector store initialized successfully")
        except Exception as e:
            logger.warning(f"Vector store initialization failed: {e}")
            vector_store = None
        
        # Initialize tool manager
        try:
            tool_manager = ToolManager(config, database, vector_store)
            await tool_manager.initialize()
            logger.info("Tool manager initialized successfully")
        except Exception as e:
            logger.warning(f"Tool manager initialization failed: {e}")
            tool_manager = None
        
        # Initialize orchestrator with all components
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
        try:
            await orchestrator.cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up orchestrator: {e}")
    
    if vector_store:
        try:
            await vector_store.cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up vector store: {e}")
    
    if tool_manager:
        try:
            if hasattr(tool_manager, 'cleanup'):
                await tool_manager.cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up tool manager: {e}")
    
    if database:
        try:
            if hasattr(database, 'close'):
                await database.close()
            elif hasattr(database, 'cleanup'):
                await database.cleanup()
        except Exception as e:
            logger.error(f"Error closing database: {e}")

# API endpoints
@app.get("/")
async def root():
    return {"message": "Ethos AI Backend is running!", "status": "healthy"}

@app.get("/health")
async def health():
    return {
        "status": "healthy", 
        "service": "ethos-ai-backend",
        "timestamp": time.time(),
        "components": {
            "database": database is not None,
            "vector_store": vector_store is not None,
            "tool_manager": tool_manager is not None,
            "orchestrator": orchestrator is not None
        }
    }

@app.post("/api/chat")
async def chat(message: ChatMessage):
    try:
        if not orchestrator:
            raise HTTPException(status_code=500, detail="Orchestrator not initialized")
        
        # Get conversation ID
        conv_id = message.conversation_id
        if not conv_id:
            # Create new conversation
            conv_id = await database.create_conversation(
                title=message.content[:50] + "..." if len(message.content) > 50 else message.content
            )
        
        # Process message with orchestrator
        response = await orchestrator.process_message(
            message.content,
            conversation_id=conv_id,
            model_override=message.model_override,
            use_tools=message.use_tools
        )
        
        # Store message in database
        await database.add_message(
            conversation_id=conv_id,
            user_message=message.content,
            ai_response=response.content,
            model_used=response.model_used,
            metadata={"tools_called": response.tools_called} if response.tools_called else None
        )
        
        return ChatResponse(
            content=response.content,
            model_used=response.model_used,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            tools_called=response.tools_called
        )
        
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/models")
async def get_models():
    try:
        if not config:
            raise HTTPException(status_code=500, detail="Config not initialized")
        
        models = []
        for model_id, model_config in config.get_enabled_models().items():
            models.append({
                "id": model_id,
                "name": model_config.name,
                "type": model_config.type,
                "provider": model_config.provider,
                "capabilities": model_config.capabilities,
                "enabled": model_config.enabled,
                "status": "available" if model_config.enabled else "disabled"
            })
        
        return {"models": models}
        
    except Exception as e:
        logger.error(f"Error getting models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/conversations")
async def create_conversation(conversation: ConversationCreate):
    try:
        if not database:
            raise HTTPException(status_code=500, detail="Database not initialized")
        
        conv_id = await database.create_conversation(conversation.title)
        conv_data = await database.get_conversation(conv_id)
        
        return ConversationResponse(
            conversation_id=conv_id,
            title=conv_data["title"],
            created_at=conv_data["created_at"]
        )
        
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/conversations")
async def get_conversations():
    try:
        if not database:
            raise HTTPException(status_code=500, detail="Database not initialized")
        
        conversations = await database.get_conversations()
        return {"conversations": conversations}
        
    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    try:
        if not database:
            raise HTTPException(status_code=500, detail="Database not initialized")
        
        conversation = await database.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        messages = await database.get_messages(conversation_id)
        conversation["messages"] = messages
        
        return conversation
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    try:
        if not database:
            raise HTTPException(status_code=500, detail="Database not initialized")
        
        await database.delete_conversation(conversation_id)
        
        # Also delete from vector store if available
        if vector_store:
            try:
                await vector_store.delete_conversation(conversation_id)
            except Exception as e:
                logger.warning(f"Error deleting from vector store: {e}")
        
        return {"message": "Conversation deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        if not tool_manager:
            raise HTTPException(status_code=500, detail="Tool manager not initialized")
        
        result = await tool_manager.process_file_upload(file)
        return result
        
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/memory/search")
async def search_memory(query: str, limit: int = 10):
    try:
        if not vector_store:
            raise HTTPException(status_code=503, detail="Vector store not available")
        
        results = await vector_store.search(query, limit=limit)
        return {"results": results}
        
    except Exception as e:
        logger.error(f"Error searching memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tools/{tool_name}")
async def execute_tool(tool_name: str, parameters: Dict[str, Any]):
    try:
        if not tool_manager:
            raise HTTPException(status_code=503, detail="Tool manager not available")
        
        result = await tool_manager.execute_tool(tool_name, parameters)
        return {"result": result}
        
    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/config")
async def get_config():
    try:
        if not config:
            raise HTTPException(status_code=500, detail="Config not initialized")
        
        return config.get_public_config()
        
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/config")
async def update_config(config_data: dict):
    try:
        if not config:
            raise HTTPException(status_code=500, detail="Config not initialized")
        
        config.update_config(config_data)
        return {"message": "Configuration updated successfully"}
        
    except Exception as e:
        logger.error(f"Error updating config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Handle WebSocket messages
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info") 