#!/usr/bin/env python3
"""
Cloud-Only Ethos AI Main Application
Fully cloud-based - no local server needed!
FORCE REDEPLOY - Railway should pick up this change
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
import subprocess
import os

# Import the cloud fusion engine
from cloud_fusion_engine import CloudEthosFusionEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Ethos AI - Cloud Edition", version="3.0.0")

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

# Initialize the Cloud Ethos Fusion Engine
try:
    fusion_engine = CloudEthosFusionEngine()
    FUSION_AVAILABLE = True
    logger.info("Cloud Ethos Fusion Engine initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Cloud Fusion Engine: {e}")
    fusion_engine = None
    FUSION_AVAILABLE = False

def check_ollama_available():
    """Check if ollama is available on Railway"""
    try:
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def get_available_models():
    """Get list of available models on Railway"""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if result.returncode == 0:
            # Parse the output to get model names
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            models = []
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if parts:
                        models.append(parts[0])
            return models
        return []
    except:
        return []

# Health check endpoint
@app.get("/")
async def root():
    ollama_available = check_ollama_available()
    available_models = get_available_models() if ollama_available else []
    
    return {
        "message": "Ethos AI - Cloud Edition",
        "status": "healthy",
        "fusion_available": FUSION_AVAILABLE,
        "ollama_available": ollama_available,
        "available_models": available_models,
        "version": "3.0.0",
        "deployment": "cloud-only"
    }

@app.get("/health")
async def health_check():
    ollama_available = check_ollama_available()
    available_models = get_available_models() if ollama_available else []
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "fusion_engine": FUSION_AVAILABLE,
        "ollama_available": ollama_available,
        "available_models": available_models,
        "deployment": "cloud-only"
    }

@app.get("/api/models")
async def get_models():
    """Get available models with cloud fusion engine status"""
    ollama_available = check_ollama_available()
    available_models = get_available_models() if ollama_available else []
    
    if FUSION_AVAILABLE and fusion_engine and ollama_available:
        try:
            # Check if our required models are available
            has_3b = "llama3.2:3b" in available_models
            has_7b = "codellama:7b" in available_models
            
            # Create Ethos model mapping
            ethos_models = [
                {
                    "id": "ethos-light",
                    "name": "Ethos Light (3B)",
                    "type": "cloud",
                    "provider": "ollama",
                    "enabled": has_3b,
                    "status": "available" if has_3b else "unavailable",
                    "ollama_model": "llama3.2:3b",
                    "capabilities": ["general_knowledge", "quick_responses", "basic_reasoning"],
                    "fusion_capable": True,
                    "reason": "Model not downloaded" if not has_3b else None
                },
                {
                    "id": "ethos-code",
                    "name": "Ethos Code (7B)",
                    "type": "cloud",
                    "provider": "ollama",
                    "enabled": has_7b,
                    "status": "available" if has_7b else "unavailable",
                    "ollama_model": "codellama:7b",
                    "capabilities": ["programming", "debugging", "code_generation", "technical_analysis"],
                    "fusion_capable": True,
                    "reason": "Model not downloaded" if not has_7b else None
                },
                {
                    "id": "ethos-pro",
                    "name": "Ethos Pro (20B) - Unavailable",
                    "type": "cloud",
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
                    "type": "cloud",
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
                "ollama_available": True,
                "available_models": available_models,
                "message": "Cloud Ethos Fusion Engine is active - running models directly on Railway",
                "deployment": "cloud-only"
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
                "type": "cloud",
                "provider": "ollama",
                "enabled": False,
                "status": "unavailable",
                "ollama_model": "llama3.2:3b",
                "capabilities": ["general_knowledge", "quick_responses", "basic_reasoning"],
                "fusion_capable": False,
                "reason": "Fusion engine not available"
            },
            {
                "id": "ethos-code",
                "name": "Ethos Code (7B)",
                "type": "cloud",
                "provider": "ollama",
                "enabled": False,
                "status": "unavailable",
                "ollama_model": "codellama:7b",
                "capabilities": ["programming", "debugging", "code_generation", "technical_analysis"],
                "fusion_capable": False,
                "reason": "Fusion engine not available"
            }
        ],
        "total": 0,
        "status": "unavailable",
        "fusion_engine": False,
        "ollama_available": check_ollama_available(),
        "available_models": get_available_models() if check_ollama_available() else [],
        "message": "Cloud fusion engine not available",
        "deployment": "cloud-only"
    }

@app.get("/api/models/status")
async def get_models_status():
    """Get detailed model status"""
    ollama_available = check_ollama_available()
    available_models = get_available_models() if ollama_available else []
    
    if FUSION_AVAILABLE and fusion_engine and ollama_available:
        try:
            # Count enabled models
            enabled_count = 0
            if "llama3.2:3b" in available_models:
                enabled_count += 1
            if "codellama:7b" in available_models:
                enabled_count += 1
            
            status_data = {
                "available": True,
                "total_models": 4,  # Total Ethos models
                "healthy_models": enabled_count,
                "available_models": available_models,
                "fusion_engine": True,
                "ollama_available": True,
                "message": f"Cloud Ethos Fusion Engine active with {enabled_count} models available",
                "capabilities": ["general_knowledge", "quick_responses", "basic_reasoning", "programming", "debugging", "code_generation", "technical_analysis"],
                "deployment": "cloud-only"
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
        "ollama_available": check_ollama_available(),
        "message": "Cloud fusion engine not available",
        "capabilities": [],
        "deployment": "cloud-only"
    }

@app.post("/api/chat")
async def chat_endpoint(request: ChatMessage):
    """Main chat endpoint using Cloud Ethos Fusion Engine"""
    start_time = time.time()
    
    if not FUSION_AVAILABLE or not fusion_engine:
        raise HTTPException(
            status_code=503, 
            detail="Cloud Ethos Fusion Engine is not available."
        )
    
    if not check_ollama_available():
        raise HTTPException(
            status_code=503,
            detail="Ollama is not available on Railway. Models may not be downloaded."
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
            "deployment": "cloud-only",
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
        "status": "created",
        "deployment": "cloud-only"
    }

@app.get("/api/conversations")
async def get_conversations():
    """Get conversation history (placeholder)"""
    return {
        "conversations": [],
        "total": 0,
        "message": "Conversation history not implemented yet",
        "deployment": "cloud-only"
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
                "available_models": get_available_models(),
                "ollama_available": check_ollama_available(),
                "message": "Cloud Ethos Fusion Engine is running and learning",
                "deployment": "cloud-only"
            }
        except Exception as e:
            logger.error(f"Error getting fusion status: {e}")
            return {
                "fusion_engine": True,
                "status": "error",
                "message": f"Error getting status: {str(e)}",
                "deployment": "cloud-only"
            }
    else:
        return {
            "fusion_engine": False,
            "status": "unavailable",
            "message": "Cloud fusion engine not initialized",
            "deployment": "cloud-only"
        }

@app.post("/api/download-models")
async def download_models():
    """Trigger model download on Railway"""
    try:
        # Run the download script
        result = subprocess.run(
            ['python', 'download_models_to_railway.py'],
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour timeout
        )
        
        if result.returncode == 0:
            return {
                "status": "success",
                "message": "Models downloaded successfully",
                "output": result.stdout,
                "deployment": "cloud-only"
            }
        else:
            return {
                "status": "error",
                "message": "Failed to download models",
                "error": result.stderr,
                "deployment": "cloud-only"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error downloading models: {str(e)}",
            "deployment": "cloud-only"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
