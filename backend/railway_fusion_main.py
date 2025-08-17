#!/usr/bin/env python3
"""
Railway-Optimized Ethos AI with Fusion Engine
Designed to work with 3B and 7B models on Railway's infrastructure
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import requests

# Import the fusion engine
from ethos_fusion_engine import EthosFusionEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Ethos AI - Railway Fusion", version="2.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400,
)

# Pydantic models
class ChatMessage(BaseModel):
    content: str
    conversation_id: Optional[str] = None
    model_override: Optional[str] = None
    use_tools: Optional[bool] = False

class ChatResponse(BaseModel):
    message: str
    conversation_id: str
    timestamp: str
    model_used: str
    confidence: float
    processing_time: float
    capabilities_used: List[str]
    synthesis_reasoning: str

# Initialize the Ethos Fusion Engine
try:
    # For Railway deployment, we'll use a tunnel URL
    # This will be updated when the tunnel is running
    fusion_engine = EthosFusionEngine(ollama_url="https://ethos-ollama.loca.lt")
    FUSION_AVAILABLE = True
    logger.info("Ethos Fusion Engine initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Fusion Engine: {e}")
    fusion_engine = None
    FUSION_AVAILABLE = False

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "Ethos AI - Railway Fusion Engine",
        "status": "healthy",
        "fusion_available": FUSION_AVAILABLE,
        "version": "2.0.0"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "fusion_engine": FUSION_AVAILABLE,
        "available_models": get_available_models_info()
    }

def get_available_models_info():
    """Get information about available models"""
    if not fusion_engine:
        return []
    
    available_models = []
    for model_name, info in fusion_engine.model_registry.items():
        if info.get("available", True):
            available_models.append({
                "name": model_name,
                "type": info["type"].value,
                "capabilities": info["capabilities"],
                "ram_required": info.get("ram_required", "unknown"),
                "status": "available"
            })
        else:
            available_models.append({
                "name": model_name,
                "type": info["type"].value,
                "capabilities": info["capabilities"],
                "ram_required": info.get("ram_required", "unknown"),
                "status": "unavailable",
                "reason": info.get("unavailable_reason", "Not available")
            })
    
    return available_models

@app.get("/api/models")
async def get_models():
    """Get available models with fusion engine status"""
    if FUSION_AVAILABLE and fusion_engine:
        try:
            available_models = get_available_models_info()
            
            # Create Ethos model mapping
            ethos_models = [
                {
                    "id": "ethos-light",
                    "name": "Ethos Light (3B)",
                    "type": "local",
                    "provider": "ollama",
                    "enabled": True,
                    "status": "available",
                    "ollama_model": "llama3.2:3b",
                    "capabilities": ["general_knowledge", "quick_responses", "basic_reasoning"],
                    "fusion_capable": True
                },
                {
                    "id": "ethos-code",
                    "name": "Ethos Code (7B)",
                    "type": "local",
                    "provider": "ollama",
                    "enabled": True,
                    "status": "available",
                    "ollama_model": "codellama:7b",
                    "capabilities": ["programming", "debugging", "code_generation", "technical_analysis"],
                    "fusion_capable": True
                },
                {
                    "id": "ethos-pro",
                    "name": "Ethos Pro (20B) - Unavailable",
                    "type": "local",
                    "provider": "ollama",
                    "enabled": False,
                    "status": "unavailable",
                    "ollama_model": "gpt-oss:20b",
                    "capabilities": ["complex_reasoning", "analysis", "research"],
                    "fusion_capable": False,
                    "reason": "Requires 25GB+ RAM - upgrade needed"
                },
                {
                    "id": "ethos-creative",
                    "name": "Ethos Creative (70B) - Unavailable",
                    "type": "local",
                    "provider": "ollama",
                    "enabled": False,
                    "status": "unavailable",
                    "ollama_model": "llama3.1:70b",
                    "capabilities": ["creative_writing", "storytelling", "artistic_expression"],
                    "fusion_capable": False,
                    "reason": "Requires 45GB+ RAM - upgrade needed"
                }
            ]
            
            response_data = {
                "models": ethos_models,
                "total": len([m for m in ethos_models if m["enabled"]]),
                "status": "available" if any(m["enabled"] for m in ethos_models) else "unavailable",
                "fusion_engine": True,
                "available_models": available_models,
                "message": "Ethos Fusion Engine is active - combining 3B and 7B models for optimal performance"
            }
        except Exception as e:
            logger.error(f"Error getting models: {e}")
            response_data = get_fallback_models()
    else:
        response_data = get_fallback_models()
    
    response = JSONResponse(content=response_data)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

def get_fallback_models():
    """Fallback models when fusion engine is not available"""
    return {
        "models": [
            {
                "id": "ethos-light",
                "name": "Ethos Light (3B)",
                "type": "local",
                "provider": "ollama",
                "enabled": False,
                "status": "unavailable",
                "ollama_model": "llama3.2:3b",
                "capabilities": ["general_knowledge", "quick_responses", "basic_reasoning"],
                "fusion_capable": False
            },
            {
                "id": "ethos-code",
                "name": "Ethos Code (7B)",
                "type": "local",
                "provider": "ollama",
                "enabled": False,
                "status": "unavailable",
                "ollama_model": "codellama:7b",
                "capabilities": ["programming", "debugging", "code_generation", "technical_analysis"],
                "fusion_capable": False
            }
        ],
        "total": 0,
        "status": "unavailable",
        "fusion_engine": False,
        "available_models": [],
        "message": "Fusion engine not available - check tunnel connection"
    }

@app.get("/api/models/status")
async def get_models_status():
    """Get detailed model status"""
    if FUSION_AVAILABLE and fusion_engine:
        try:
            available_models = get_available_models_info()
            enabled_models = [m for m in available_models if m["status"] == "available"]
            
            status_data = {
                "available": True,
                "total_models": len(available_models),
                "healthy_models": len(enabled_models),
                "available_models": [m["name"] for m in enabled_models],
                "fusion_engine": True,
                "message": f"Ethos Fusion Engine active with {len(enabled_models)} models available",
                "capabilities": list(set([cap for m in enabled_models for cap in m["capabilities"]]))
            }
        except Exception as e:
            logger.error(f"Error getting model status: {e}")
            status_data = get_fallback_status()
    else:
        status_data = get_fallback_status()
    
    response = JSONResponse(content=status_data)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

def get_fallback_status():
    """Fallback status when fusion engine is not available"""
    return {
        "available": False,
        "total_models": 0,
        "healthy_models": 0,
        "available_models": [],
        "fusion_engine": False,
        "message": "Fusion engine not available",
        "capabilities": []
    }

@app.post("/api/chat")
async def chat_endpoint(request: ChatMessage):
    """Main chat endpoint using Ethos Fusion Engine"""
    start_time = time.time()
    
    if not FUSION_AVAILABLE or not fusion_engine:
        raise HTTPException(
            status_code=503, 
            detail="Ethos Fusion Engine is not available. Please check your tunnel connection."
        )
    
    try:
        # Generate unified response using fusion engine
        ethos_response = await fusion_engine.generate_unified_response(
            message=request.content,
            context={"model_override": request.model_override}
        )
        
        processing_time = time.time() - start_time
        
        # Create response
        chat_response = ChatResponse(
            message=ethos_response.final_response,
            conversation_id=request.conversation_id or str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
            model_used=", ".join(ethos_response.source_models),
            confidence=ethos_response.confidence,
            processing_time=processing_time,
            capabilities_used=ethos_response.capabilities_used,
            synthesis_reasoning=ethos_response.reasoning
        )
        
        response_data = {
            "message": chat_response.message,
            "conversation_id": chat_response.conversation_id,
            "timestamp": chat_response.timestamp,
            "model_used": chat_response.model_used,
            "confidence": chat_response.confidence,
            "processing_time": chat_response.processing_time,
            "capabilities_used": chat_response.capabilities_used,
            "synthesis_reasoning": chat_response.synthesis_reasoning,
            "fusion_engine": True,
            "status": "success"
        }
        
        response = JSONResponse(content=response_data)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating response: {str(e)}"
        )

@app.post("/api/conversations")
async def create_conversation():
    """Create a new conversation"""
    conversation_id = str(uuid.uuid4())
    return {
        "conversation_id": conversation_id,
        "created_at": datetime.now().isoformat(),
        "status": "created"
    }

@app.get("/api/conversations")
async def get_conversations():
    """Get conversation history (placeholder)"""
    return {
        "conversations": [],
        "total": 0,
        "message": "Conversation history not implemented yet"
    }

@app.get("/api/fusion/status")
async def get_fusion_status():
    """Get detailed fusion engine status"""
    if FUSION_AVAILABLE and fusion_engine:
        try:
            learning_summary = fusion_engine.get_learning_summary()
            return {
                "fusion_engine": True,
                "status": "active",
                "total_interactions": learning_summary["total_interactions"],
                "performance_trend": learning_summary["performance_trends"]["trend"],
                "capabilities_used": len(learning_summary["capability_insights"]),
                "available_models": get_available_models_info(),
                "message": "Ethos Fusion Engine is running and learning"
            }
        except Exception as e:
            logger.error(f"Error getting fusion status: {e}")
            return {
                "fusion_engine": True,
                "status": "error",
                "message": f"Error getting status: {str(e)}"
            }
    else:
        return {
            "fusion_engine": False,
            "status": "unavailable",
            "message": "Fusion engine not initialized"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
