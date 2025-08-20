#!/usr/bin/env python3
"""
Test script for embedded AI server
"""

import sys
import os

# Add backend directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backend_dir = os.path.join(parent_dir, 'backend')
sys.path.insert(0, backend_dir)

def test_import():
    """Test if we can import the server module"""
    try:
        from client_storage_version import app
        print("✅ Successfully imported client_storage_version")
        return True
    except Exception as e:
        print(f"❌ Failed to import client_storage_version: {e}")
        print(f"📁 Current directory: {os.getcwd()}")
        print(f"📁 Backend directory: {backend_dir}")
        print(f"📁 Files in backend: {os.listdir(backend_dir) if os.path.exists(backend_dir) else 'Directory not found'}")
        return False

def test_ollama():
    """Test if Ollama is working"""
    try:
        import subprocess
        result = subprocess.run(
            ['ollama', 'list'], 
            capture_output=True, 
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        if result.returncode == 0:
            print("✅ Ollama is working")
            print(f"📋 Available models:\n{result.stdout}")
            return True
        else:
            print(f"❌ Ollama error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Ollama test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Embedded AI Server")
    print("=" * 40)
    
    # Test imports
    import_ok = test_import()
    
    # Test Ollama
    ollama_ok = test_ollama()
    
    if import_ok and ollama_ok:
        print("\n✅ All tests passed! Server should work.")
    else:
        print("\n❌ Some tests failed. Check the issues above.")
