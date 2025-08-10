from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Ethos AI", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    content: str
    conversation_id: str = None
    model_override: str = None
    use_tools: bool = True

class ChatResponse(BaseModel):
    content: str
    model_used: str = "local"
    timestamp: str = "2024-01-01T00:00:00Z"
    tools_called: list = []

@app.get("/")
async def root():
    return {"message": "Ethos AI Backend is running!", "status": "healthy"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "ethos-ai-backend"}

@app.post("/api/chat")
async def chat(message: ChatMessage):
    try:
        # Simple echo response for testing
        response = ChatResponse(
            content=f"Echo: {message.content}",
            model_used="test-model",
            timestamp="2024-01-01T00:00:00Z"
        )
        return response
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/models")
async def get_models():
    return {
        "models": [
            {"id": "llama3-70b", "name": "LLaMA 3 70B", "type": "local", "enabled": True},
            {"id": "deepseek-r1", "name": "DeepSeek R1", "type": "local", "enabled": True},
            {"id": "codellama", "name": "CodeLLaMA", "type": "local", "enabled": True}
        ]
    }

if __name__ == "__main__":
    logger.info("Starting Ethos AI backend...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info") 