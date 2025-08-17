#!/usr/bin/env python3
"""
Setup script to install Ollama on Railway
This runs during the build process
"""

import os
import subprocess
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def install_ollama():
    """Install Ollama on Railway"""
    try:
        logger.info("🚀 Installing Ollama on Railway...")
        
        # Install Ollama using the official install script
        install_script = """
        curl -fsSL https://ollama.ai/install.sh | sh
        """
        
        result = subprocess.run(
            install_script,
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info("✅ Ollama installed successfully")
            return True
        else:
            logger.error(f"❌ Failed to install Ollama: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error installing Ollama: {e}")
        return False

def verify_ollama():
    """Verify Ollama is working"""
    try:
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"✅ Ollama version: {result.stdout.strip()}")
            return True
        else:
            logger.error("❌ Ollama not found")
            return False
    except Exception as e:
        logger.error(f"❌ Error verifying Ollama: {e}")
        return False

def main():
    """Main setup function"""
    logger.info("🔧 Setting up Ollama for Railway deployment")
    
    # Check if we're on Railway
    if os.getenv('RAILWAY_ENVIRONMENT'):
        logger.info("🚂 Running on Railway - installing Ollama")
        
        if install_ollama():
            if verify_ollama():
                logger.info("🎉 Ollama setup complete!")
                return True
            else:
                logger.error("❌ Ollama verification failed")
                return False
        else:
            logger.error("❌ Ollama installation failed")
            return False
    else:
        logger.info("💻 Running locally - skipping Ollama installation")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
