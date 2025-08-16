from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
import logging
import requests
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Ethos AI - Local Ollama Backend")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    model_override: str = "ethos-light"
    conversation_id: str = None
    use_tools: bool = False

def get_ollama_response(message: str, model_id: str = "ethos-light") -> str:
    """Get response from local Ollama models"""
    try:
        # Map Ethos model names to actual Ollama models (using user's installed models)
        model_mapping = {
            "ethos-light": "llama3.2:3b",  # Use the 3B model for light responses
            "ethos-code": "codellama:7b",  # Use CodeLlama for programming
            "ethos-pro": "gpt-oss:20b",  # Use the 20B model for advanced responses
            "ethos-creative": "llama3.1:70b"  # Use the 70B model for creative tasks
        }
        
        # Get the actual Ollama model name
        ollama_model = model_mapping.get(model_id.lower(), "llama3.2:3b")
        
        # Connect to local Ollama instance
        ollama_url = "http://localhost:11434/api/generate"
        
        payload = {
            "model": ollama_model,
            "prompt": message,
            "stream": False
        }
        
        logger.info(f"Requesting response from Ollama model: {ollama_model}")
        
        # Make request to Ollama
        response = requests.post(ollama_url, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result.get("response", "I'm sorry, I couldn't generate a response.")
            logger.info(f"Successfully got response from {ollama_model}")
            return ai_response
        else:
            logger.error(f"Ollama request failed: {response.status_code}")
            return f"Error: Ollama request failed with status {response.status_code}"
            
    except requests.exceptions.ConnectionError:
        logger.error("Cannot connect to Ollama. Is it running on localhost:11434?")
        return "Error: Cannot connect to Ollama. Please make sure Ollama is running on localhost:11434"
    except Exception as e:
        logger.error(f"Error getting Ollama response: {e}")
        return f"Error: {str(e)}"

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Ethos AI Local Backend is running!",
        "status": "healthy",
        "version": "1.0.0",
        "mode": "local-ollama",
        "privacy": "100% local - using your Ollama models",
        "timestamp": time.time()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ethos-ai-local-backend",
        "mode": "local-ollama",
        "ollama_available": check_ollama_availability()
    }

def check_ollama_availability():
    """Check if Ollama is available"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

@app.get("/api/models")
async def get_models():
    """Get available models from Ollama"""
    try:
        # Check what models are available in Ollama
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        
        if response.status_code == 200:
            ollama_models = response.json().get("models", [])
            
            # Map available models to Ethos models
            models = []
            for model in ollama_models:
                model_name = model.get("name", "")
                if "llama3.2" in model_name.lower():
                    models.append({
                        "id": "ethos-light",
                        "name": "Ethos Light",
                        "type": "local",
                        "provider": "ollama",
                        "ollama_model": model_name,
                        "enabled": True,
                        "status": "available"
                    })
                elif "codellama" in model_name.lower():
                    models.append({
                        "id": "ethos-code", 
                        "name": "Ethos Code",
                        "type": "local",
                        "provider": "ollama",
                        "ollama_model": model_name,
                        "enabled": True,
                        "status": "available"
                    })
                elif "gpt-oss" in model_name.lower():
                    models.append({
                        "id": "ethos-pro",
                        "name": "Ethos Pro", 
                        "type": "local",
                        "provider": "ollama",
                        "ollama_model": model_name,
                        "enabled": True,
                        "status": "available"
                    })
                elif "llama3.1" in model_name.lower():
                    models.append({
                        "id": "ethos-creative",
                        "name": "Ethos Creative",
                        "type": "local",
                        "provider": "ollama",
                        "ollama_model": model_name,
                        "enabled": True,
                        "status": "available"
                    })
            
            return {
                "models": models,
                "total": len(models),
                "status": "available",
                "ollama_models": [m.get("name") for m in ollama_models]
            }
        else:
            return {
                "models": [],
                "total": 0,
                "status": "unavailable",
                "error": "Cannot connect to Ollama"
            }
            
    except Exception as e:
        logger.error(f"Error getting models: {e}")
        return {
            "models": [],
            "total": 0,
            "status": "error",
            "error": str(e)
        }

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Chat endpoint using local Ollama models"""
    try:
        logger.info(f"Chat request: {request.message} with model: {request.model_override}")
        
        # Get response from Ollama
        ai_response = get_ollama_response(request.message, request.model_override)
        
        return {
            "content": ai_response,
            "model_used": request.model_override,
            "timestamp": time.time(),
            "privacy": "100% local processing with Ollama"
        }
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Ethos AI Local Backend...")
    print("📡 Connecting to local Ollama instance...")
    print("🔒 Privacy-First: All processing happens locally!")
    uvicorn.run(app, host="0.0.0.0", port=8000)
