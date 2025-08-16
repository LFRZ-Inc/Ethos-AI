import requests
import time
import logging
import json
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class WebhookRelay:
    """Webhook relay for Railway to local Ollama communication"""
    
    def __init__(self):
        self.webhook_url = None
        self.local_ollama_url = "http://localhost:11434"
        self.model_mapping = {
            "ethos-light": "llama3.2:3b",
            "ethos-code": "codellama:7b", 
            "ethos-pro": "gpt-oss:20b",
            "ethos-creative": "llama3.1:70b"
        }
    
    def create_webhook(self) -> str:
        """Create a webhook endpoint"""
        try:
            response = requests.post("https://webhook.site/token", timeout=10)
            if response.status_code == 200:
                token = response.json().get("token")
                webhook_url = f"https://webhook.site/{token}"
                self.webhook_url = webhook_url
                logger.info(f"Created webhook: {webhook_url}")
                return webhook_url
            else:
                logger.error("Failed to create webhook")
                return None
        except Exception as e:
            logger.error(f"Error creating webhook: {e}")
            return None
    
    def send_request_to_webhook(self, message: str, model_id: str = "ethos-light") -> bool:
        """Send request to webhook for local processing"""
        try:
            if not self.webhook_url:
                return False
            
            payload = {
                "type": "ollama_request",
                "message": message,
                "model_id": model_id,
                "timestamp": time.time()
            }
            
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Error sending to webhook: {e}")
            return False
    
    def process_local_request(self, message: str, model_id: str = "ethos-light") -> Optional[str]:
        """Process request locally with Ollama"""
        try:
            # Map Ethos model to actual Ollama model
            ollama_model = self.model_mapping.get(model_id.lower(), "llama3.2:3b")
            
            # Create payload for local Ollama
            payload = {
                "model": ollama_model,
                "prompt": message,
                "stream": False
            }
            
            # Send to local Ollama
            response = requests.post(
                f"{self.local_ollama_url}/api/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get("response", "")
                logger.info(f"Got response from {ollama_model}")
                return ai_response
            else:
                logger.error(f"Ollama request failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error processing local request: {e}")
            return None
    
    def get_available_models(self) -> list:
        """Get list of available Ollama models"""
        try:
            response = requests.get(f"{self.local_ollama_url}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [model.get("name") for model in data.get("models", [])]
            return []
        except Exception as e:
            logger.error(f"Error getting models: {e}")
            return []

# Global webhook relay
webhook_relay = WebhookRelay()
