"""
Ollama model connector for Ethos AI
Handles local models via Ollama API
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any
import httpx

from .base_model import BaseModel, ModelResponse

logger = logging.getLogger(__name__)

class OllamaModel(BaseModel):
    """Ollama model connector"""
    
    def __init__(self, config):
        super().__init__(config)
        self.endpoint = config.endpoint or "http://localhost:11434"
        self.model_name = config.parameters.get("model", "llama3.2:70b")
        self.temperature = config.parameters.get("temperature", 0.7)
        self.max_tokens = config.parameters.get("max_tokens", 4096)
        self.client = None
        
    async def initialize(self) -> bool:
        """Initialize the Ollama client"""
        try:
            self.client = httpx.AsyncClient(timeout=60.0)
            
            # Test connection
            response = await self.client.get(f"{self.endpoint}/api/tags")
            if response.status_code == 200:
                logger.info(f"Ollama connection established for {self.model_id}")
                return True
            else:
                logger.error(f"Failed to connect to Ollama: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error initializing Ollama model {self.model_id}: {e}")
            return False
    
    async def generate(
        self, 
        prompt: str, 
        context: List[Dict] = None,
        use_tools: bool = True
    ) -> ModelResponse:
        """Generate response using Ollama"""
        start_time = time.time()
        
        try:
            # Format the prompt with context and Ethos identity
            formatted_prompt = self._format_prompt(prompt, context)
            
            # Prepare request payload
            payload = {
                "model": self.model_name,
                "prompt": formatted_prompt,
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens,
                    "top_p": 0.9,
                    "top_k": 40,
                    "repeat_penalty": 1.1
                }
            }
            
            # Make request to Ollama
            response = await self.client.post(
                f"{self.endpoint}/api/generate",
                json=payload
            )
            
            if response.status_code != 200:
                raise Exception(f"Ollama API error: {response.status_code}")
            
            result = response.json()
            
            # Extract response content
            content = result.get("response", "")
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            return ModelResponse(
                content=content,
                model_used=self.model_id,
                tokens_used=result.get("eval_count", 0),
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Error generating response with Ollama {self.model_id}: {e}")
            raise
    
    def _format_prompt(self, prompt: str, context: List[Dict] = None) -> str:
        """Format prompt with context for Ollama"""
        formatted_prompt = ""
        
        # Add Ethos system message
        formatted_prompt += self.get_ethos_system_message() + "\n\n"
        
        # Add conversation context
        if context:
            formatted_prompt += "CONVERSATION HISTORY:\n" + self.format_context(context) + "\n"
        
        # Add current prompt
        formatted_prompt += f"User: {prompt}\nAssistant: "
        
        return formatted_prompt
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.client:
            await self.client.aclose()
            self.client = None
    
    async def list_models(self) -> List[str]:
        """List available models in Ollama"""
        try:
            response = await self.client.get(f"{self.endpoint}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
            return []
        except Exception as e:
            logger.error(f"Error listing Ollama models: {e}")
            return []
    
    async def pull_model(self, model_name: str) -> bool:
        """Pull a model from Ollama"""
        try:
            payload = {"name": model_name}
            response = await self.client.post(
                f"{self.endpoint}/api/pull",
                json=payload
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error pulling model {model_name}: {e}")
            return False 