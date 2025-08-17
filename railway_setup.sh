#!/bin/bash
# Railway Setup Script - Install Ollama

echo "🚀 Railway Setup: Installing Ollama..."

# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Verify installation
if command -v ollama &> /dev/null; then
    echo "✅ Ollama installed successfully"
    ollama --version
else
    echo "❌ Ollama installation failed"
    exit 1
fi

echo "🎉 Railway setup complete!"
