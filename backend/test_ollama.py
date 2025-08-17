#!/usr/bin/env python3
"""
Test script to check Ollama and download models on Railway
"""

import subprocess
import os
import sys

def test_ollama():
    """Test if Ollama is working"""
    print("🔍 Testing Ollama installation...")
    
    try:
        # Check Ollama version
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Ollama version: {result.stdout.strip()}")
        else:
            print(f"❌ Ollama not working: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error checking Ollama: {e}")
        return False
    
    return True

def list_models():
    """List available models"""
    print("📋 Listing available models...")
    
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if result.returncode == 0:
            print("Available models:")
            print(result.stdout)
            return result.stdout
        else:
            print(f"❌ Error listing models: {result.stderr}")
            return ""
    except Exception as e:
        print(f"❌ Error listing models: {e}")
        return ""

def download_model(model_name):
    """Download a specific model"""
    print(f"📥 Downloading {model_name}...")
    
    try:
        result = subprocess.run(
            ['ollama', 'pull', model_name],
            capture_output=True,
            text=True,
            timeout=1800  # 30 minutes
        )
        
        if result.returncode == 0:
            print(f"✅ {model_name} downloaded successfully")
            return True
        else:
            print(f"❌ Failed to download {model_name}: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"❌ Timeout downloading {model_name}")
        return False
    except Exception as e:
        print(f"❌ Error downloading {model_name}: {e}")
        return False

def main():
    print("🚀 Railway Ollama Test Script")
    print("=" * 40)
    
    # Test Ollama
    if not test_ollama():
        print("❌ Ollama not available, exiting")
        sys.exit(1)
    
    # List current models
    list_models()
    
    # Download 3B model
    print("\n" + "=" * 40)
    if download_model("llama3.2:3b"):
        print("✅ 3B model download successful")
    else:
        print("❌ 3B model download failed")
    
    # List models again
    print("\n" + "=" * 40)
    list_models()
    
    print("\n🎉 Test completed!")

if __name__ == "__main__":
    main()
