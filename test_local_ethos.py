import requests
import json

def test_local_ethos():
    """Test the local Ethos AI backend with Ollama models"""
    
    print("🧪 Testing Local Ethos AI Backend...")
    print("=" * 50)
    
    # Test 1: Health check
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
            health_data = response.json()
            print(f"   Ollama available: {health_data.get('ollama_available', 'Unknown')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to local backend: {e}")
        print("   Make sure the backend is running: python backend/local_main.py")
        return
    
    # Test 2: Get available models
    try:
        response = requests.get("http://localhost:8000/api/models", timeout=10)
        if response.status_code == 200:
            models_data = response.json()
            print(f"✅ Models endpoint working")
            print(f"   Total models: {models_data.get('total', 0)}")
            print(f"   Status: {models_data.get('status', 'Unknown')}")
            
            ollama_models = models_data.get('ollama_models', [])
            if ollama_models:
                print("   Available Ollama models:")
                for model in ollama_models:
                    print(f"     - {model}")
            else:
                print("   No Ollama models detected")
        else:
            print(f"❌ Models endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting models: {e}")
    
    # Test 3: Test chat with Ethos Light
    try:
        chat_data = {
            "message": "Hello! What model are you?",
            "model_override": "ethos-light"
        }
        
        print("\n🧠 Testing chat with Ethos Light (llama3.2:3b)...")
        response = requests.post("http://localhost:8000/api/chat", 
                               json=chat_data, timeout=30)
        
        if response.status_code == 200:
            chat_response = response.json()
            print("✅ Chat test successful!")
            print(f"   Model used: {chat_response.get('model_used', 'Unknown')}")
            print(f"   Response: {chat_response.get('content', 'No content')[:100]}...")
        else:
            print(f"❌ Chat test failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Error in chat test: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Test completed!")

if __name__ == "__main__":
    test_local_ethos()
