#!/usr/bin/env python3
"""
Ethos AI Status Checker
Checks if all systems are working properly
"""

import requests
import json
import time

def check_tunnel():
    """Check if localtunnel is working"""
    try:
        response = requests.get("https://ethos-ollama.loca.lt/api/tags", timeout=10)
        if response.status_code == 200:
            data = response.json()
            models = [model.get("name") for model in data.get("models", [])]
            print(f"✅ Tunnel working - {len(models)} models available")
            return True
        else:
            print(f"❌ Tunnel error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Tunnel not accessible: {e}")
        return False

def check_cloud_server():
    """Check if cloud server is working"""
    try:
        # Check health
        response = requests.get("https://cooking-ethos-ai-production-6bfd.up.railway.app/health", timeout=10)
        if response.status_code == 200:
            print("✅ Cloud server health: OK")
        else:
            print(f"❌ Cloud server health error: {response.status_code}")
            return False
        
        # Check models
        response = requests.get("https://cooking-ethos-ai-production-6bfd.up.railway.app/api/models", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Cloud server models: {data.get('total', 0)} available")
        else:
            print(f"❌ Cloud server models error: {response.status_code}")
            return False
        
        # Check status
        response = requests.get("https://cooking-ethos-ai-production-6bfd.up.railway.app/api/models/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("available"):
                print("✅ Cloud server status: Available")
                return True
            else:
                print("❌ Cloud server status: Unavailable")
                return False
        else:
            print(f"❌ Cloud server status error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Cloud server error: {e}")
        return False

def check_frontend():
    """Check if frontend is accessible"""
    try:
        response = requests.get("https://ethos-ai-phi.vercel.app", timeout=10)
        if response.status_code == 200:
            print("✅ Frontend: Accessible")
            return True
        else:
            print(f"❌ Frontend error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend error: {e}")
        return False

def test_ai_response():
    """Test a real AI response"""
    try:
        payload = {
            "message": "Hello! What model are you?",
            "model_override": "ethos-light"
        }
        
        response = requests.post(
            "https://cooking-ethos-ai-production-6bfd.up.railway.app/api/chat",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data.get("content", "")
            print(f"✅ AI Response: {content[:100]}...")
            return True
        else:
            print(f"❌ AI Response error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ AI Response error: {e}")
        return False

def main():
    """Main status check"""
    print("🔍 Ethos AI Status Check")
    print("=" * 40)
    
    # Check all systems
    tunnel_ok = check_tunnel()
    cloud_ok = check_cloud_server()
    frontend_ok = check_frontend()
    ai_ok = test_ai_response()
    
    print("\n" + "=" * 40)
    print("📊 Summary:")
    print(f"   Tunnel: {'✅ Working' if tunnel_ok else '❌ Failed'}")
    print(f"   Cloud Server: {'✅ Working' if cloud_ok else '❌ Failed'}")
    print(f"   Frontend: {'✅ Working' if frontend_ok else '❌ Failed'}")
    print(f"   AI Responses: {'✅ Working' if ai_ok else '❌ Failed'}")
    
    if all([tunnel_ok, cloud_ok, frontend_ok, ai_ok]):
        print("\n🎉 All systems are working perfectly!")
        print("🌐 Your Ethos AI is fully functional!")
    else:
        print("\n⚠️  Some systems need attention.")
        if not tunnel_ok:
            print("   - Start localtunnel: lt --port 11434 --subdomain ethos-ollama")
        if not cloud_ok:
            print("   - Check Railway deployment")
        if not frontend_ok:
            print("   - Check Vercel deployment")

if __name__ == "__main__":
    main()
