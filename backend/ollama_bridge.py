import requests
import time
import logging
from typing import Optional, Dict, Any
from tunnel_setup import tunnel_manager

logger = logging.getLogger(__name__)

class OllamaBridge:
    """Bridge to connect cloud server to local Ollama models"""
    
    def __init__(self, ollama_url: str = None):
        # Use the localtunnel URL - this should work better with Railway
        self.ollama_url = ollama_url or "https://ethos-ollama.loca.lt"
        self.model_mapping = {
            "ethos-light": "llama3.2:3b",
            "ethos-code": "codellama:7b", 
            "ethos-pro": "gpt-oss:20b",
            "ethos-creative": "llama3.1:70b"
        }
        
        # Headers for requests
        self.headers = {
            "User-Agent": "Ethos-AI-Cloud/1.0"
        }
        
        # Try to setup tunnel on initialization
        if not tunnel_manager.is_active:
            tunnel_manager.setup_tunnel()
            self.ollama_url = tunnel_manager.get_ollama_url()
    
    def is_available(self) -> bool:
        """Check if Ollama is available"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", headers=self.headers, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_available_models(self) -> list:
        """Get list of available Ollama models"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [model.get("name") for model in data.get("models", [])]
            return []
        except Exception as e:
            logger.error(f"Error getting Ollama models: {e}")
            return []
    
    def generate_response(self, message: str, model_id: str = "ethos-light") -> Optional[str]:
        """Generate response using local Ollama model"""
        try:
            # Map Ethos model to actual Ollama model
            ollama_model = self.model_mapping.get(model_id.lower(), "llama3.2:3b")
            
            # Check if model is available
            available_models = self.get_available_models()
            if ollama_model not in available_models:
                logger.warning(f"Model {ollama_model} not available. Available: {available_models}")
                return None
            
            # Generate response
            payload = {
                "model": ollama_model,
                "prompt": message,
                "stream": False
            }
            
            logger.info(f"Requesting response from {ollama_model}")
            response = requests.post(
                f"{self.ollama_url}/api/generate", 
                json=payload, 
                headers=self.headers,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get("response", "")
                logger.info(f"Successfully got response from {ollama_model}")
                return ai_response
            else:
                logger.error(f"Ollama request failed: {response.status_code}")
                return None
                
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to Ollama. Is it running?")
            return None
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return None
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about available models"""
        try:
            available_models = self.get_available_models()
            
            models = []
            for ethos_id, ollama_model in self.model_mapping.items():
                if ollama_model in available_models:
                    models.append({
                        "id": ethos_id,
                        "name": f"Ethos {ethos_id.split('-')[1].title()}",
                        "type": "local",
                        "provider": "ollama",
                        "ollama_model": ollama_model,
                        "enabled": True,
                        "status": "available"
                    })
            
            return {
                "models": models,
                "total": len(models),
                "status": "available" if models else "unavailable",
                "ollama_available": self.is_available(),
                "ollama_models": available_models
            }
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return {
                "models": [],
                "total": 0,
                "status": "error",
                "ollama_available": False,
                "error": str(e)
            }
