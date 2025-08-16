#!/usr/bin/env python3
"""
Setup script for Cloud Ethos AI with Local Ollama Models
"""

import requests
import time
import subprocess
import sys
import os

def check_ollama_running():
    """Check if Ollama is running locally"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama is running locally")
            return True
        else:
            print("❌ Ollama is not responding")
            return False
    except:
        print("❌ Cannot connect to Ollama")
        return False

def get_ollama_models():
    """Get list of available Ollama models"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        if response.status_code == 200:
            data = response.json()
            models = [model.get("name") for model in data.get("models", [])]
            print(f"📦 Found {len(models)} Ollama models:")
            for model in models:
                print(f"   - {model}")
            return models
        return []
    except Exception as e:
        print(f"❌ Error getting models: {e}")
        return []

def test_cloud_connection():
    """Test connection to cloud server"""
    cloud_url = "https://cooking-ethos-ai-production-6bfd.up.railway.app"
    try:
        response = requests.get(f"{cloud_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Cloud server is accessible")
            return True
        else:
            print(f"❌ Cloud server error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to cloud server: {e}")
        return False

def setup_ngrok():
    """Setup ngrok tunnel"""
    print("\n🌐 Setting up ngrok tunnel...")
    print("This will expose your local Ollama to the internet")
    
    # Check if ngrok is installed
    try:
        result = subprocess.run(["ngrok", "version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ ngrok is installed")
        else:
            print("❌ ngrok not found")
            print("Please install ngrok from https://ngrok.com/")
            return None
    except FileNotFoundError:
        print("❌ ngrok not found")
        print("Please install ngrok from https://ngrok.com/")
        return None
    
    # Start ngrok tunnel
    try:
        print("🚀 Starting ngrok tunnel on port 11434...")
        process = subprocess.Popen(
            ["ngrok", "http", "11434"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment for ngrok to start
        time.sleep(3)
        
        # Get the public URL
        try:
            response = requests.get("http://localhost:4040/api/tunnels", timeout=5)
            if response.status_code == 200:
                tunnels = response.json().get("tunnels", [])
                if tunnels:
                    public_url = tunnels[0].get("public_url")
                    if public_url:
                        print(f"✅ ngrok tunnel active: {public_url}")
                        return public_url.replace("https://", "http://")
        except:
            pass
        
        print("⚠️  ngrok tunnel started but URL not detected")
        print("Please check ngrok dashboard at http://localhost:4040")
        return None
        
    except Exception as e:
        print(f"❌ Error starting ngrok: {e}")
        return None

def main():
    """Main setup function"""
    print("🚀 Setting up Cloud Ethos AI with Local Ollama Models")
    print("=" * 60)
    
    # Step 1: Check Ollama
    print("\n1️⃣  Checking Ollama...")
    if not check_ollama_running():
        print("❌ Please start Ollama first:")
        print("   ollama serve")
        return
    
    # Step 2: Get models
    print("\n2️⃣  Checking Ollama models...")
    models = get_ollama_models()
    if not models:
        print("❌ No models found. Please download some models:")
        print("   ollama pull llama3.2:3b")
        print("   ollama pull gpt-oss:20b")
        return
    
    # Step 3: Check cloud server
    print("\n3️⃣  Checking cloud server...")
    if not test_cloud_connection():
        print("❌ Cannot connect to cloud server")
        return
    
    # Step 4: Setup tunnel
    print("\n4️⃣  Setting up tunnel...")
    tunnel_url = setup_ngrok()
    
    if tunnel_url:
        print(f"\n🎉 Setup complete!")
        print(f"🌐 Your Ollama models are now accessible via: {tunnel_url}")
        print(f"☁️  Cloud server will use your local models")
        print(f"\n📝 Next steps:")
        print(f"   1. Deploy the updated backend to Railway")
        print(f"   2. Test the cloud server with your models")
        print(f"   3. Enjoy real AI responses from anywhere!")
    else:
        print("\n⚠️  Manual tunnel setup required")
        print("Please set up ngrok or similar tunnel service")
        print("Then update the tunnel URL in the backend")

if __name__ == "__main__":
    main()
