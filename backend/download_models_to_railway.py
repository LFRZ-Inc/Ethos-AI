#!/usr/bin/env python3
"""
Railway Model Downloader
Downloads 3B and 7B models directly to Railway's storage
"""

import os
import subprocess
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_railway_environment():
    """Check if we're running on Railway"""
    return os.getenv('RAILWAY_ENVIRONMENT') is not None

def download_model(model_name: str):
    """Download a model using ollama"""
    try:
        logger.info(f"🔄 Downloading {model_name}...")
        
        # Use subprocess to run ollama pull
        result = subprocess.run(
            ['ollama', 'pull', model_name],
            capture_output=True,
            text=True,
            timeout=1800  # 30 minutes timeout
        )
        
        if result.returncode == 0:
            logger.info(f"✅ Successfully downloaded {model_name}")
            return True
        else:
            logger.error(f"❌ Failed to download {model_name}: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error(f"⏰ Timeout downloading {model_name}")
        return False
    except Exception as e:
        logger.error(f"❌ Error downloading {model_name}: {e}")
        return False

def main():
    """Main download function"""
    logger.info("🚀 Starting Railway Model Download")
    
    # Check if we're on Railway
    if not check_railway_environment():
        logger.warning("⚠️ Not running on Railway - this script is designed for Railway deployment")
    
    # Models to download (3B and 7B only)
    models_to_download = [
        "llama3.2:3b",    # Ethos Light
        "codellama:7b"    # Ethos Code
    ]
    
    logger.info(f"📦 Will download {len(models_to_download)} models")
    
    # Download each model
    successful_downloads = []
    failed_downloads = []
    
    for model in models_to_download:
        if download_model(model):
            successful_downloads.append(model)
        else:
            failed_downloads.append(model)
    
    # Summary
    logger.info("📊 Download Summary:")
    logger.info(f"✅ Successful: {successful_downloads}")
    logger.info(f"❌ Failed: {failed_downloads}")
    
    if successful_downloads:
        logger.info("🎉 Railway models are ready! Ethos AI can now run completely in the cloud.")
    else:
        logger.error("💥 No models downloaded successfully")
        sys.exit(1)

if __name__ == "__main__":
    main()
