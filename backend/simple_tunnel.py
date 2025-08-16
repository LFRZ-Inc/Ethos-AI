import requests
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class SimpleTunnel:
    """Simple tunnel solution for local Ollama access"""
    
    def __init__(self):
        self.tunnel_url = None
        self.is_active = False
    
    def setup_tunnel(self) -> bool:
        """Setup simple tunnel - for now, just use localhost"""
        try:
            logger.info("Setting up simple tunnel to local Ollama...")
            
            # For now, we'll use localhost
            # In a real deployment, you'd need to:
            # 1. Use ngrok: ngrok http 11434
            # 2. Or use cloudflared: cloudflared tunnel --url http://localhost:11434
            # 3. Or deploy Ollama to a cloud service
            
            test_url = "http://localhost:11434/api/tags"
            
            try:
                response = requests.get(test_url, timeout=5)
                if response.status_code == 200:
                    logger.info("Direct connection to local Ollama successful")
                    self.tunnel_url = "http://localhost:11434"
                    self.is_active = True
                    return True
            except:
                pass
            
            logger.warning("Direct connection failed. Need tunnel setup.")
            logger.info("Please set up one of the following:")
            logger.info("1. ngrok: ngrok http 11434")
            logger.info("2. cloudflared: cloudflared tunnel --url http://localhost:11434")
            logger.info("3. Or deploy Ollama to Railway/other cloud service")
            
            return False
            
        except Exception as e:
            logger.error(f"Error setting up tunnel: {e}")
            return False
    
    def get_ollama_url(self) -> str:
        """Get the Ollama URL"""
        if self.tunnel_url:
            return self.tunnel_url
        return "http://localhost:11434"

# Global tunnel manager
simple_tunnel = SimpleTunnel()
