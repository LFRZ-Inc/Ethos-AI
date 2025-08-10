#!/bin/bash

# Ethos AI Installation Script
# This script sets up the complete Ethos AI environment

set -e

echo "🚀 Installing Ethos AI..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    OS="windows"
else
    print_error "Unsupported operating system: $OSTYPE"
    exit 1
fi

print_status "Detected OS: $OS"

# Check Python version
print_status "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.11+ first."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
print_success "Python version: $PYTHON_VERSION"

# Check Node.js version
print_status "Checking Node.js version..."
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

NODE_VERSION=$(node --version)
print_success "Node.js version: $NODE_VERSION"

# Install Python dependencies
print_status "Installing Python dependencies..."
cd backend
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
cd ..
print_success "Python dependencies installed"

# Install Node.js dependencies
print_status "Installing Node.js dependencies..."
cd frontend
npm install
cd ..
print_success "Node.js dependencies installed"

# Install Ollama
print_status "Installing Ollama..."
if ! command -v ollama &> /dev/null; then
    if [[ "$OS" == "linux" ]]; then
        curl -fsSL https://ollama.ai/install.sh | sh
    elif [[ "$OS" == "macos" ]]; then
        curl -fsSL https://ollama.ai/install.sh | sh
    else
        print_warning "Please install Ollama manually from https://ollama.ai"
    fi
else
    print_success "Ollama is already installed"
fi

# Create data directories
print_status "Creating data directories..."
mkdir -p ~/EthosAIData/{conversations,embeddings,models,uploads,exports,logs}
print_success "Data directories created"

# Create configuration
print_status "Setting up configuration..."
mkdir -p ~/.ethos_ai/config
if [[ ! -f ~/.ethos_ai/config/config.yaml ]]; then
    cp backend/config/config.example.yaml ~/.ethos_ai/config/config.yaml 2>/dev/null || true
    print_success "Configuration file created at ~/.ethos_ai/config/config.yaml"
else
    print_success "Configuration file already exists"
fi

# Download models (optional)
read -p "Do you want to download local models now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Downloading local models..."
    if command -v ollama &> /dev/null; then
        ollama pull llama3.2:70b &
        ollama pull deepseek-coder:33b &
        ollama pull llava:latest &
        wait
        print_success "Local models downloaded"
    else
        print_warning "Ollama not found, skipping model download"
    fi
fi

# Create desktop shortcut (Linux/macOS)
if [[ "$OS" == "linux" || "$OS" == "macos" ]]; then
    print_status "Creating desktop shortcut..."
    cat > ~/Desktop/EthosAI.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Ethos AI
Comment=Local-first hybrid AI interface
Exec=$(pwd)/scripts/start.sh
Icon=$(pwd)/frontend/src-tauri/icons/icon.png
Terminal=false
Categories=Development;AI;
EOF
    chmod +x ~/Desktop/EthosAI.desktop
    print_success "Desktop shortcut created"
fi

print_success "🎉 Ethos AI installation completed!"
echo
print_status "Next steps:"
echo "1. Edit ~/.ethos_ai/config/config.yaml to add your API keys"
echo "2. Run './scripts/start.sh' to start the application"
echo "3. Open http://localhost:1420 in your browser"
echo
print_status "For more information, see the README.md file" 