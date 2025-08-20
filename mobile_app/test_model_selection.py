#!/usr/bin/env python3
"""
Test model selection for embedded AI server
"""

import sys
import os

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from mobile_app.embedded_ai_server import EmbeddedAIServer

def test_model_selection():
    """Test the model selection logic"""
    print("🧪 Testing Model Selection")
    print("=" * 40)
    
    # Create server instance
    server = EmbeddedAIServer()
    
    # Get device specs
    specs = server.get_device_specs()
    print(f"📱 Device: {specs['platform']} {specs['architecture']}")
    print(f"💾 Memory: {specs['memory']['available_gb']}GB available")
    print(f"💿 Storage: {specs['storage']['free_gb']}GB available")
    
    # Get available Ollama models
    available_models = server.get_available_ollama_models()
    print(f"\n📋 Available Ollama models:")
    for model in available_models:
        print(f"  ✅ {model}")
    
    # Get selected models
    selected_models = server.select_models_for_device()
    print(f"\n🤖 Selected models for device:")
    for model in selected_models:
        print(f"  🎯 {model['name']} ({model['type']}, {model['size_gb']}GB)")
    
    # Test download_models
    print(f"\n🚀 Testing model preparation...")
    success = server.download_models()
    
    if success:
        print(f"✅ Success! {len(server.models_available)} models ready")
        print(f"📊 Models available:")
        for model in server.models_available:
            print(f"  🎯 {model['name']} ({model['type']})")
    else:
        print("❌ Failed to prepare models")
    
    return success

if __name__ == "__main__":
    test_model_selection()
