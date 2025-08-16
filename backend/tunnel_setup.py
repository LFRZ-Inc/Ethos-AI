import requests
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class TunnelManager:
    """Manage tunnel to expose local Ollama to cloud"""
    
    def __init__(self):
        self.tunnel_url = None
        self.is_active = False
    
    def setup_tunnel(self) -> bool:
        """Setup tunnel using ngrok or similar service"""
        try:
            # For now, we'll use a simple approach
            # In production, you'd use ngrok, cloudflared, or similar
            logger.info("Setting up tunnel to local Ollama...")
            
            # Check if we can access local Ollama directly
            # This works if the cloud server is on the same network
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
            
            # If direct connection fails, we need a proper tunnel
            logger.warning("Direct connection failed. Need proper tunnel setup.")
            logger.info("Please set up ngrok or similar tunnel service.")
            logger.info("Example: ngrok http 11434")
            
            return False
            
        except Exception as e:
            logger.error(f"Error setting up tunnel: {e}")
            return False
    
    def get_ollama_url(self) -> str:
        """Get the Ollama URL (local or tunneled)"""
        if self.tunnel_url:
            return self.tunnel_url
        return "http://localhost:11434"

# Global tunnel manager
tunnel_manager = TunnelManager()
