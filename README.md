# Ethos AI - Local-First Hybrid AI Interface

A powerful, privacy-focused AI interface that runs entirely on your device, combining local models with cloud APIs for optimal performance.

## 🚀 **Quick Start - Run Locally**

This is a **local-first application** that runs on your computer. It's not a web app - you need to run it locally to use it.

### **Option 1: Simple Setup (Recommended)**
```bash
# 1. Clone the repository
git clone https://github.com/LFRZ-Inc/Ethos-AI.git
cd Ethos-AI

# 2. Install backend dependencies
cd backend
pip install -r requirements.txt

# 3. Install frontend dependencies  
cd ../frontend
npm install

# 4. Start the application
# Terminal 1: Start backend
cd backend
python main.py

# Terminal 2: Start frontend (in new terminal)
cd frontend
npm run dev
```

### **Option 2: Use the Mock Backend (Easiest)**
If you don't have AI models set up yet:
```bash
# Start with mock backend (no AI models needed)
cd backend
python simple_main.py

# Start frontend
cd ../frontend
npm run dev
```

## 🌐 **Access the Application**

Once running, open your browser and go to:
- **Frontend**: http://localhost:1420
- **Backend API**: http://localhost:8000

## 📱 **What You'll See**

- **Chat Interface**: Send messages and get AI responses
- **Model Selection**: Choose between different AI models
- **Conversation History**: Save and manage your chats
- **Settings**: Configure API keys and preferences
- **File Upload**: Upload documents for analysis

## 🔧 **Features**

- **Multi-Model Orchestration**: Intelligent routing between local and cloud models
- **Local-First Architecture**: All data stored locally, works offline
- **Multi-Modal Support**: Text, image, and audio processing
- **Vector Memory**: Persistent, searchable conversation history
- **Tool Calling**: Code execution, web search, file analysis
- **Cross-Platform**: Windows, macOS, and Linux support

## 🤖 **Models Supported**

### Local Models (via Ollama/LM Studio)
- LLaMA 3 70B (quantized) - General chat
- DeepSeek-R1 - Math and logic
- CodeLLaMA - Programming assistance
- LLaVA-Next - Image analysis
- Flux.1 - Image generation

### Cloud APIs
- Claude 3.5 Sonnet - Deep reasoning and writing
- OpenAI GPT-4 - Fallback option

## 📋 **Prerequisites**

- Python 3.11+
- Node.js 18+
- Ollama (for local models) - Optional
- 16GB+ RAM recommended

## 🔑 **Configuration**

### API Keys (Optional)
For cloud models, add your API keys in the Settings page:
- **Anthropic API Key** - For Claude models
- **OpenAI API Key** - For GPT models
- **Hugging Face Token** - For HF models

### Local Models Setup
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull required models
ollama pull llama3.2:70b
ollama pull deepseek-coder:33b
ollama pull llava:latest
```

## 📁 **Project Structure**

```
Ethos-AI/
├── frontend/                 # React UI
├── backend/                  # Python orchestration
│   ├── models/              # Model connectors
│   ├── memory/              # Vector store & embeddings
│   ├── tools/               # Tool calling implementations
│   └── config/              # Configuration files
├── memory/                   # Local data storage
├── docs/                     # Documentation
└── scripts/                  # Build and deployment scripts
```

## 🛠 **Development**

### Backend Development
```bash
cd backend
python main.py
```

### Frontend Development
```bash
cd frontend
npm run dev
```

### Building for Distribution
```bash
cd frontend
npm run build
```

## 🔒 **Privacy & Data**

- **All data stored locally** on your device
- **No data sent to external servers** (except when using cloud APIs)
- **Vector database** for semantic search of your conversations
- **SQLite database** for conversation storage

## 🆘 **Troubleshooting**

### Common Issues:
1. **Port 1420 or 8000 in use**: Kill existing processes or change ports
2. **Python dependencies**: Make sure you're in the backend directory when installing
3. **Node modules**: Run `npm install` in the frontend directory
4. **AI models not working**: Use the mock backend (`simple_main.py`) for testing

### Getting Help:
- Check the console for error messages
- Make sure both backend and frontend are running
- Try the mock backend first to test the UI

## 📄 **License**

MIT License - see LICENSE file for details.

---

**Note**: This is a local application. The GitHub repository shows the README by default - this is normal. To use the application, you need to clone and run it locally on your computer. 