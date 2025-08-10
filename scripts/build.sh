#!/bin/bash

# Ethos AI Build Script
# This script builds the application for distribution

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

print_status "Building for: $OS"

# Check if we're in the right directory
if [[ ! -f "backend/main.py" ]] || [[ ! -f "frontend/package.json" ]]; then
    print_error "Please run this script from the Ethos AI root directory"
    exit 1
fi

# Build backend
print_status "Building backend..."
cd backend

# Create virtual environment if it doesn't exist
if [[ ! -d "venv" ]]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
print_status "Installing Python dependencies..."
pip install -r requirements.txt

# Create executable
print_status "Creating backend executable..."
pip install pyinstaller
pyinstaller --onefile --name ethos-ai-backend main.py

cd ..

# Build frontend
print_status "Building frontend..."
cd frontend

# Install dependencies
print_status "Installing Node.js dependencies..."
npm install

# Build Tauri application
print_status "Building Tauri application..."
npm run tauri build

cd ..

# Create distribution package
print_status "Creating distribution package..."
DIST_DIR="dist/ethos-ai-$OS"
mkdir -p "$DIST_DIR"

# Copy backend executable
cp backend/dist/ethos-ai-backend "$DIST_DIR/"

# Copy Tauri build
cp -r frontend/src-tauri/target/release/bundle/* "$DIST_DIR/"

# Copy scripts
cp scripts/start.sh "$DIST_DIR/"
chmod +x "$DIST_DIR/start.sh"

# Copy configuration
mkdir -p "$DIST_DIR/config"
cp backend/config/config.example.yaml "$DIST_DIR/config/"

# Create README
cat > "$DIST_DIR/README.txt" << EOF
Ethos AI - Local-First Hybrid AI Interface

Installation:
1. Extract this archive
2. Run ./start.sh to start the application
3. Open http://localhost:1420 in your browser

Configuration:
- Edit config/config.yaml to add your API keys
- All data is stored in ~/EthosAIData/

Requirements:
- Python 3.11+
- Node.js 18+
- Ollama (for local models)

For more information, visit: https://github.com/your-repo/ethos-ai
EOF

# Create archive
print_status "Creating archive..."
cd dist
tar -czf "ethos-ai-$OS.tar.gz" "ethos-ai-$OS"
cd ..

print_success "🎉 Build completed!"
print_status "Distribution package: dist/ethos-ai-$OS.tar.gz" 