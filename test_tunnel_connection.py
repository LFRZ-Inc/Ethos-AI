#!/usr/bin/env python3
"""
Test tunnel connection to local Ollama
"""

import requests
import json

def test_tunnel():
    """Test the ngrok tunnel connection"""
    
    tunnel_url = "https://604e179881c8.ngrok-free.app"
    headers = {
        "ngrok-skip-browser-warning": "true",
        "User-Agent": "Ethos-AI-Cloud/1.0"
    }
    
    print("🧪 Testing ngrok tunnel connection...")
    print(f"🌐 Tunnel URL: {tunnel_url}")
    print("=" * 50)
    
    # Test 1: Check if tunnel is accessible
    try:
        print("1️⃣  Testing tunnel accessibility...")
        response = requests.get(f"{tunnel_url}/api/tags", headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ Tunnel is accessible!")
            data = response.json()
            models = [model.get("name") for model in data.get("models", [])]
            print(f"📦 Found {len(models)} models:")
            for model in models:
                print(f"   - {model}")
        else:
            print(f"❌ Tunnel returned status: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Error accessing tunnel: {e}")
        return False
    
    # Test 2: Test AI response generation
    try:
        print("\n2️⃣  Testing AI response generation...")
        payload = {
            "model": "llama3.2:3b",
            "prompt": "Hello! What model are you?",
            "stream": False
        }
        
        response = requests.post(
            f"{tunnel_url}/api/generate",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result.get("response", "")
            print("✅ AI response generated successfully!")
            print(f"🤖 Response: {ai_response[:100]}...")
        else:
            print(f"❌ AI generation failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Error generating AI response: {e}")
        return False
    
    # Test 3: Test from cloud server perspective
    try:
        print("\n3️⃣  Testing from cloud server perspective...")
        cloud_url = "https://cooking-ethos-ai-production-6bfd.up.railway.app"
        
        response = requests.get(f"{cloud_url}/api/models", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Cloud server is responding!")
            print(f"   Models available: {data.get('total', 0)}")
            print(f"   Ollama available: {data.get('ollama_available', False)}")
            
            if data.get('ollama_available'):
                print("🎉 Cloud server can access your local Ollama!")
                return True
            else:
                print("⚠️  Cloud server cannot access Ollama")
                return False
        else:
            print(f"❌ Cloud server error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing cloud server: {e}")
        return False

if __name__ == "__main__":
    success = test_tunnel()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! Your tunnel is working perfectly!")
        print("🚀 Your cloud server should now use real AI responses!")
    else:
        print("❌ Some tests failed. Check the tunnel setup.")
        print("💡 Make sure ngrok is running and the URL is correct.")
