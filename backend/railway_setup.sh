#!/bin/bash

# Railway startup script for Ethos AI
echo "🚀 Starting Ethos AI on Railway..."

# Install Ollama if not already installed
if ! command -v ollama &> /dev/null; then
    echo "📦 Installing Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
    echo "✅ Ollama installed successfully"
else
    echo "✅ Ollama already installed"
fi

# Start Ollama service in background
echo "🚀 Starting Ollama service..."
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to start
echo "⏳ Waiting for Ollama to start..."
sleep 10

# Check if Ollama is running
if kill -0 $OLLAMA_PID 2>/dev/null; then
    echo "✅ Ollama service started successfully"
else
    echo "❌ Failed to start Ollama service"
    exit 1
fi

# Start the Python application
echo "🚀 Starting Python application..."
exec gunicorn main:app --bind 0.0.0.0:$PORT --workers 1 --timeout 600
