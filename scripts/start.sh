#!/bin/bash

# Ethos AI Startup Script
# This script starts both the backend and frontend

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

# Function to cleanup on exit
cleanup() {
    print_status "Shutting down Ethos AI..."
    if [[ -n $BACKEND_PID ]]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [[ -n $FRONTEND_PID ]]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Check if we're in the right directory
if [[ ! -f "backend/main.py" ]] || [[ ! -f "frontend/package.json" ]]; then
    print_error "Please run this script from the Ethos AI root directory"
    exit 1
fi

print_status "Starting Ethos AI..."

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    print_warning "Ollama is not running. Starting Ollama..."
    if command -v ollama &> /dev/null; then
        ollama serve &
        sleep 3
    else
        print_error "Ollama is not installed. Please install Ollama first."
        exit 1
    fi
fi

# Start backend
print_status "Starting backend server..."
cd backend
python3 main.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Check if backend is running
if ! curl -s http://localhost:8000/ > /dev/null 2>&1; then
    print_error "Backend failed to start"
    exit 1
fi

print_success "Backend started successfully"

# Start frontend
print_status "Starting frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
sleep 5

# Check if frontend is running
if ! curl -s http://localhost:1420 > /dev/null 2>&1; then
    print_warning "Frontend may not be ready yet"
else
    print_success "Frontend started successfully"
fi

print_success "🎉 Ethos AI is now running!"
echo
print_status "Access the application at:"
echo "  Frontend: http://localhost:1420"
echo "  Backend API: http://localhost:8000"
echo
print_status "Press Ctrl+C to stop the application"

# Wait for user to stop
wait 