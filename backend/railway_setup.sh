#!/bin/bash
# Railway Setup Script - Install Ollama

echo "🚀 Railway Setup: Installing Ollama..."

# Check if Ollama is already installed
if command -v ollama &> /dev/null; then
    echo "✅ Ollama already installed"
    ollama --version
else
    echo "📦 Installing Ollama..."
    # Install Ollama
    curl -fsSL https://ollama.ai/install.sh | sh
    
    # Verify installation
    if command -v ollama &> /dev/null; then
        echo "✅ Ollama installed successfully"
        ollama --version
    else
        echo "❌ Ollama installation failed"
        echo "⚠️ Continuing without Ollama..."
    fi
fi

echo "🎉 Railway setup complete!"
