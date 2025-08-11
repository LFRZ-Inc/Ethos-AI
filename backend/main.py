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
from memory.semantic_search import SemanticSearch
from models.orchestrator import ModelOrchestrator
from tools.tool_manager import ToolManager
from agents.task_automation import TaskAutomation
from processors.document_processor import DocumentProcessor, KnowledgeBase, CitationSystem
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
semantic_search: Optional[SemanticSearch] = None
task_automation: Optional[TaskAutomation] = None
document_processor: Optional[DocumentProcessor] = None
knowledge_base: Optional[KnowledgeBase] = None
citation_system: Optional[CitationSystem] = None

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
    global config, orchestrator, vector_store, database, tool_manager, semantic_search, task_automation, document_processor, knowledge_base, citation_system
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
        orchestrator.database = database  # Pass database for conversation context
        await orchestrator.initialize()
        
        # Initialize semantic search
        semantic_search = SemanticSearch(database)
        logger.info("Semantic search system initialized")
        
        # Initialize task automation
        task_automation = TaskAutomation(database, orchestrator)
        logger.info("Task automation system initialized")
        
        # Initialize document processing and knowledge base
        document_processor = DocumentProcessor(orchestrator)
        knowledge_base = KnowledgeBase(database)
        citation_system = CitationSystem()
        logger.info("Document processing and knowledge base systems initialized")
        
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

@app.put("/api/conversations/{conversation_id}/title")
async def update_conversation_title(conversation_id: str, title_data: dict):
    try:
        if not database:
            raise HTTPException(status_code=500, detail="Database not initialized")
        
        new_title = title_data.get("title")
        if not new_title:
            raise HTTPException(status_code=400, detail="Title is required")
        
        success = await database.update_conversation_title(conversation_id, new_title)
        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return {"message": "Conversation title updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating conversation title: {e}")
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
        # Use semantic search if available
        if semantic_search:
            results = await semantic_search.search_conversations(query, limit=limit)
            return {"results": [vars(result) for result in results]}
        # Fallback to unified memory
        elif orchestrator and orchestrator.unified_memory:
            results = await orchestrator.unified_memory.search_memory(query, limit=limit)
            return {"results": results}
        # Fallback to vector store
        elif vector_store:
            results = await vector_store.search(query, limit=limit)
            return {"results": results}
        else:
            raise HTTPException(status_code=503, detail="Memory system not available")
        
    except Exception as e:
        logger.error(f"Error searching memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/memory/analytics")
async def get_memory_analytics():
    """Get comprehensive analytics about all conversations"""
    try:
        if not semantic_search:
            raise HTTPException(status_code=503, detail="Semantic search not available")
        
        analytics = await semantic_search.get_memory_analytics()
        return {
            "total_conversations": analytics.total_conversations,
            "total_messages": analytics.total_messages,
            "average_messages_per_conversation": analytics.average_messages_per_conversation,
            "most_active_day": analytics.most_active_day,
            "most_active_hour": analytics.most_active_hour,
            "top_topics": analytics.top_topics,
            "conversation_timeline": analytics.conversation_timeline,
            "model_usage": analytics.model_usage,
            "average_response_length": analytics.average_response_length,
            "memory_growth_rate": analytics.memory_growth_rate
        }
        
    except Exception as e:
        logger.error(f"Error getting memory analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/conversations/{conversation_id}/insights")
async def get_conversation_insights(conversation_id: str):
    """Get insights about a specific conversation"""
    try:
        if not semantic_search:
            raise HTTPException(status_code=503, detail="Semantic search not available")
        
        insights = await semantic_search.get_conversation_insights(conversation_id)
        return insights
        
    except Exception as e:
        logger.error(f"Error getting conversation insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/memory/search/advanced")
async def advanced_search(
    query: str, 
    limit: int = 10,
    conversation_filter: Optional[str] = None,
    date_filter: Optional[str] = None,
    topic_filter: Optional[str] = None
):
    """Advanced semantic search with filters"""
    try:
        if not semantic_search:
            raise HTTPException(status_code=503, detail="Semantic search not available")
        
        results = await semantic_search.search_conversations(
            query=query,
            limit=limit,
            conversation_filter=conversation_filter,
            date_filter=date_filter
        )
        
        # Apply topic filter if specified
        if topic_filter:
            results = [r for r in results if topic_filter in r.topics]
        
        return {"results": [vars(result) for result in results]}
        
    except Exception as e:
        logger.error(f"Error in advanced search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Task Automation Endpoints
@app.post("/api/tasks")
async def create_task(task_data: dict):
    """Create a new automated task"""
    try:
        if not task_automation:
            raise HTTPException(status_code=503, detail="Task automation not available")
        
        task = await task_automation.create_task(task_data)
        return {
            "task_id": task.id,
            "name": task.name,
            "status": task.status.value,
            "message": f"Task '{task.name}' created successfully"
        }
        
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tasks")
async def get_tasks(status: Optional[str] = None):
    """Get all tasks, optionally filtered by status"""
    try:
        if not task_automation:
            raise HTTPException(status_code=503, detail="Task automation not available")
        
        tasks = await task_automation.get_tasks()
        if status:
            tasks = [t for t in tasks if t.status.value == status]
        
        return {
            "tasks": [
                {
                    "id": task.id,
                    "name": task.name,
                    "description": task.description,
                    "status": task.status.value,
                    "task_type": task.task_type.value,
                    "created_at": task.created_at,
                    "started_at": task.started_at,
                    "completed_at": task.completed_at,
                    "priority": task.priority,
                    "tags": task.tags,
                    "steps_count": len(task.steps)
                }
                for task in tasks
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str):
    """Get a specific task by ID"""
    try:
        if not task_automation:
            raise HTTPException(status_code=503, detail="Task automation not available")
        
        task = await task_automation.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return {
            "id": task.id,
            "name": task.name,
            "description": task.description,
            "status": task.status.value,
            "task_type": task.task_type.value,
            "created_at": task.created_at,
            "scheduled_for": task.scheduled_for,
            "started_at": task.started_at,
            "completed_at": task.completed_at,
            "priority": task.priority,
            "tags": task.tags,
            "metadata": task.metadata,
            "result": task.result,
            "error": task.error,
            "steps": [
                {
                    "id": step.id,
                    "name": step.name,
                    "action": step.action,
                    "status": step.status.value,
                    "result": step.result,
                    "error": step.error,
                    "start_time": step.start_time,
                    "end_time": step.end_time,
                    "retry_count": step.retry_count
                }
                for step in task.steps
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tasks/{task_id}/execute")
async def execute_task(task_id: str):
    """Execute a task immediately"""
    try:
        if not task_automation:
            raise HTTPException(status_code=503, detail="Task automation not available")
        
        task = await task_automation.execute_task(task_id)
        return {
            "task_id": task.id,
            "name": task.name,
            "status": task.status.value,
            "result": task.result,
            "message": f"Task '{task.name}' executed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error executing task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/tasks/{task_id}")
async def cancel_task(task_id: str):
    """Cancel a running task"""
    try:
        if not task_automation:
            raise HTTPException(status_code=503, detail="Task automation not available")
        
        success = await task_automation.cancel_task(task_id)
        if not success:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return {"message": f"Task {task_id} cancelled successfully"}
        
    except Exception as e:
        logger.error(f"Error cancelling task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tasks/templates")
async def get_task_templates():
    """Get available task templates"""
    templates = [
        {
            "name": "File Analysis Workflow",
            "description": "Analyze and summarize multiple files",
            "template": {
                "name": "File Analysis Workflow",
                "description": "Analyze and summarize multiple files",
                "type": "workflow",
                "steps": [
                    {
                        "name": "Process File",
                        "action": "process_file",
                        "parameters": {
                            "file_path": "{{file_path}}",
                            "operation": "analyze"
                        }
                    },
                    {
                        "name": "Generate Summary",
                        "action": "process_file",
                        "parameters": {
                            "file_path": "{{file_path}}",
                            "operation": "summarize"
                        },
                        "dependencies": ["step_1"]
                    }
                ]
            }
        },
        {
            "name": "Research Assistant",
            "description": "Research a topic and generate a report",
            "template": {
                "name": "Research Assistant",
                "description": "Research a topic and generate a report",
                "type": "workflow",
                "steps": [
                    {
                        "name": "Web Search",
                        "action": "web_search",
                        "parameters": {
                            "query": "{{research_topic}}",
                            "max_results": 10
                        }
                    },
                    {
                        "name": "Generate Report",
                        "action": "content_generation",
                        "parameters": {
                            "type": "report",
                            "topic": "{{research_topic}}",
                            "length": "comprehensive"
                        },
                        "dependencies": ["step_1"]
                    }
                ]
            }
        },
        {
            "name": "Scheduled Reminder",
            "description": "Set up a scheduled reminder",
            "template": {
                "name": "Scheduled Reminder",
                "description": "Set up a scheduled reminder",
                "type": "scheduled",
                "scheduled_for": "{{reminder_time}}",
                "steps": [
                    {
                        "name": "Send Reminder",
                        "action": "send_notification",
                        "parameters": {
                            "message": "{{reminder_message}}",
                            "type": "reminder"
                        }
                    }
                ]
            }
        },
        {
            "name": "Data Analysis Pipeline",
            "description": "Analyze data and generate insights",
            "template": {
                "name": "Data Analysis Pipeline",
                "description": "Analyze data and generate insights",
                "type": "workflow",
                "steps": [
                    {
                        "name": "Load Data",
                        "action": "data_extraction",
                        "parameters": {
                            "source": "{{data_source}}",
                            "type": "structured"
                        }
                    },
                    {
                        "name": "Analyze Data",
                        "action": "data_analysis",
                        "parameters": {
                            "data_source": "{{data_source}}",
                            "analysis_type": "comprehensive"
                        },
                        "dependencies": ["step_1"]
                    },
                    {
                        "name": "Generate Report",
                        "action": "content_generation",
                        "parameters": {
                            "type": "analysis_report",
                            "topic": "Data Analysis Results",
                            "length": "detailed"
                        },
                        "dependencies": ["step_2"]
                    }
                ]
            }
        }
    ]
    
    return {"templates": templates}

# Document Processing and Knowledge Base Endpoints
@app.post("/api/documents/process")
async def process_document(file: UploadFile = File(...)):
    """Process and analyze a document"""
    try:
        if not document_processor:
            raise HTTPException(status_code=503, detail="Document processor not available")
        
        # Save uploaded file temporarily
        temp_file_path = f"/tmp/{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process the document
        metadata = await document_processor.process_document(temp_file_path, content)
        
        # Clean up temp file
        os.remove(temp_file_path)
        
        return {
            "filename": metadata.filename,
            "file_type": metadata.file_type,
            "file_size": metadata.file_size,
            "pages": metadata.pages,
            "word_count": metadata.word_count,
            "processing_time": metadata.processing_time,
            "summary": metadata.summary,
            "keywords": metadata.keywords,
            "topics": metadata.topics,
            "language": metadata.language,
            "confidence": metadata.confidence,
            "extracted_text": metadata.extracted_text[:1000] + "..." if len(metadata.extracted_text) > 1000 else metadata.extracted_text,
            "error": metadata.error
        }
        
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/documents/supported-formats")
async def get_supported_formats():
    """Get list of supported document formats"""
    if not document_processor:
        raise HTTPException(status_code=503, detail="Document processor not available")
    
    return {
        "supported_formats": document_processor.supported_formats,
        "pdf_available": PDF_AVAILABLE if 'PDF_AVAILABLE' in globals() else False,
        "ocr_available": OCR_AVAILABLE if 'OCR_AVAILABLE' in globals() else False,
        "docx_available": DOCX_AVAILABLE if 'DOCX_AVAILABLE' in globals() else False,
        "pandas_available": PANDAS_AVAILABLE if 'PANDAS_AVAILABLE' in globals() else False
    }

@app.post("/api/knowledge/entries")
async def add_knowledge_entry(entry_data: dict):
    """Add a new knowledge base entry"""
    try:
        if not knowledge_base:
            raise HTTPException(status_code=503, detail="Knowledge base not available")
        
        entry = await knowledge_base.add_entry(
            title=entry_data['title'],
            content=entry_data['content'],
            source=entry_data['source'],
            document_id=entry_data.get('document_id'),
            tags=entry_data.get('tags', [])
        )
        
        return {
            "id": entry.id,
            "title": entry.title,
            "source": entry.source,
            "tags": entry.tags,
            "created_at": entry.created_at.isoformat(),
            "message": f"Knowledge entry '{entry.title}' added successfully"
        }
        
    except Exception as e:
        logger.error(f"Error adding knowledge entry: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/knowledge/entries")
async def search_knowledge_entries(query: str = "", limit: int = 10):
    """Search knowledge base entries"""
    try:
        if not knowledge_base:
            raise HTTPException(status_code=503, detail="Knowledge base not available")
        
        if query:
            entries = await knowledge_base.search_entries(query, limit)
        else:
            # Return all entries if no query
            entries = list(knowledge_base.entries.values())[:limit]
        
        return {
            "entries": [
                {
                    "id": entry.id,
                    "title": entry.title,
                    "content": entry.content[:200] + "..." if len(entry.content) > 200 else entry.content,
                    "source": entry.source,
                    "tags": entry.tags,
                    "created_at": entry.created_at.isoformat(),
                    "updated_at": entry.updated_at.isoformat()
                }
                for entry in entries
            ],
            "total": len(entries)
        }
        
    except Exception as e:
        logger.error(f"Error searching knowledge entries: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/knowledge/entries/{entry_id}")
async def get_knowledge_entry(entry_id: str):
    """Get a specific knowledge base entry"""
    try:
        if not knowledge_base:
            raise HTTPException(status_code=503, detail="Knowledge base not available")
        
        entry = await knowledge_base.get_entry(entry_id)
        if not entry:
            raise HTTPException(status_code=404, detail="Knowledge entry not found")
        
        return {
            "id": entry.id,
            "title": entry.title,
            "content": entry.content,
            "source": entry.source,
            "document_id": entry.document_id,
            "tags": entry.tags,
            "created_at": entry.created_at.isoformat(),
            "updated_at": entry.updated_at.isoformat(),
            "metadata": entry.metadata
        }
        
    except Exception as e:
        logger.error(f"Error getting knowledge entry: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/knowledge/entries/{entry_id}")
async def update_knowledge_entry(entry_id: str, updates: dict):
    """Update a knowledge base entry"""
    try:
        if not knowledge_base:
            raise HTTPException(status_code=503, detail="Knowledge base not available")
        
        success = await knowledge_base.update_entry(entry_id, updates)
        if not success:
            raise HTTPException(status_code=404, detail="Knowledge entry not found")
        
        return {"message": f"Knowledge entry {entry_id} updated successfully"}
        
    except Exception as e:
        logger.error(f"Error updating knowledge entry: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/knowledge/entries/{entry_id}")
async def delete_knowledge_entry(entry_id: str):
    """Delete a knowledge base entry"""
    try:
        if not knowledge_base:
            raise HTTPException(status_code=503, detail="Knowledge base not available")
        
        success = await knowledge_base.delete_entry(entry_id)
        if not success:
            raise HTTPException(status_code=404, detail="Knowledge entry not found")
        
        return {"message": f"Knowledge entry {entry_id} deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting knowledge entry: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/knowledge/tags")
async def get_knowledge_tags():
    """Get all unique tags from knowledge base"""
    try:
        if not knowledge_base:
            raise HTTPException(status_code=503, detail="Knowledge base not available")
        
        tags = await knowledge_base.get_all_tags()
        return {"tags": tags}
        
    except Exception as e:
        logger.error(f"Error getting knowledge tags: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/knowledge/entries/tag/{tag}")
async def get_entries_by_tag(tag: str):
    """Get all knowledge base entries with a specific tag"""
    try:
        if not knowledge_base:
            raise HTTPException(status_code=503, detail="Knowledge base not available")
        
        entries = await knowledge_base.get_entries_by_tag(tag)
        
        return {
            "entries": [
                {
                    "id": entry.id,
                    "title": entry.title,
                    "content": entry.content[:200] + "..." if len(entry.content) > 200 else entry.content,
                    "source": entry.source,
                    "tags": entry.tags,
                    "created_at": entry.created_at.isoformat()
                }
                for entry in entries
            ],
            "tag": tag,
            "count": len(entries)
        }
        
    except Exception as e:
        logger.error(f"Error getting entries by tag: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/citations")
async def add_citation(citation_data: dict):
    """Add a new citation"""
    try:
        if not citation_system:
            raise HTTPException(status_code=503, detail="Citation system not available")
        
        citation_id = citation_system.add_citation(
            source=citation_data['source'],
            content=citation_data['content'],
            metadata=citation_data.get('metadata', {})
        )
        
        return {
            "citation_id": citation_id,
            "message": "Citation added successfully"
        }
        
    except Exception as e:
        logger.error(f"Error adding citation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/citations/{citation_id}")
async def get_citation(citation_id: str):
    """Get a citation by ID"""
    try:
        if not citation_system:
            raise HTTPException(status_code=503, detail="Citation system not available")
        
        citation = citation_system.get_citation(citation_id)
        if not citation:
            raise HTTPException(status_code=404, detail="Citation not found")
        
        return citation
        
    except Exception as e:
        logger.error(f"Error getting citation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/citations/search")
async def search_citations(query: str):
    """Search citations"""
    try:
        if not citation_system:
            raise HTTPException(status_code=503, detail="Citation system not available")
        
        citations = citation_system.search_citations(query)
        return {"citations": citations}
        
    except Exception as e:
        logger.error(f"Error searching citations: {e}")
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
    uvicorn.run(app, host="0.0.0.0", port=8003, log_level="info") 