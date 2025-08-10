# Ethos AI - Local-First Hybrid AI Interface

A powerful, privacy-focused AI interface that runs entirely on your device, combining local models with cloud APIs for optimal performance.

## 📋 **Setup Checklist**

### **Required (Must Have):**
- [ ] **Python 3.11+** installed
- [ ] **Node.js 18+** installed  
- [ ] **Git** installed
- [ ] **16GB+ RAM** (recommended)
- [ ] **Internet connection** (for initial setup)

### **Optional (For Full Features):**
- [ ] **Ollama** installed (for local AI models)
- [ ] **Anthropic API key** (for Claude models)
- [ ] **OpenAI API key** (for GPT models)
- [ ] **Hugging Face token** (for HF models)

### **Mobile Support:**
- [ ] **iPhone 15 Pro Max**: ✅ Works via web browser
- [ ] **Samsung Z Fold 4**: ✅ Works via web browser
- [ ] **Android/iOS**: ✅ Works via web browser

## 🚀 **Quick Start**

### **1. Clone & Setup**
```bash
git clone https://github.com/LFRZ-Inc/Ethos-AI.git
cd Ethos-AI
```

### **2. Install Backend**
```bash
cd backend
pip install -r requirements.txt
```

### **3. Install Frontend**
```bash
cd ../frontend
npm install
```

### **4. Start Application**
```bash
# Terminal 1: Start backend
cd backend
python main.py

# Terminal 2: Start frontend (new terminal)
cd frontend
npm run dev
```

### **5. Access**
- **Desktop**: http://localhost:1420
- **Mobile**: http://YOUR_COMPUTER_IP:1420
- **API**: http://localhost:8000

## 📱 **Mobile Access Setup**

### **For iPhone 15 Pro Max & Samsung Z Fold 4:**

1. **Find your computer's IP address:**
   ```bash
   # Windows
   ipconfig
   
   # Mac/Linux
   ifconfig
   ```

2. **Allow firewall access:**
   - Windows: Allow Python and Node.js through firewall
   - Mac: Allow incoming connections

3. **Access on mobile:**
   - iPhone: Open Safari, go to `http://YOUR_IP:1420`
   - Samsung: Open Chrome, go to `http://YOUR_IP:1420`

4. **Add to home screen:**
   - iPhone: Share → Add to Home Screen
   - Samsung: Menu → Add to Home Screen

### **Mobile Features:**
- ✅ **Responsive design** - Works on all screen sizes
- ✅ **Touch-friendly** - Optimized for mobile interaction
- ✅ **PWA ready** - Can be installed as app
- ✅ **Offline capable** - Works without internet once loaded

## 🔧 **Features**

- **Multi-Model Orchestration**: Intelligent routing between local and cloud models
- **Local-First Architecture**: All data stored locally, works offline
- **Multi-Modal Support**: Text, image, and audio processing
- **Vector Memory**: Persistent, searchable conversation history
- **Tool Calling**: Code execution, web search, file analysis
- **Cross-Platform**: Windows, macOS, Linux, iOS, Android
- **Mobile Optimized**: Responsive design for phones and tablets

## 🤖 **Models Supported**

### Local Models (via Ollama)
- LLaMA 3 70B (quantized) - General chat
- DeepSeek-R1 - Math and logic
- CodeLLaMA - Programming assistance
- LLaVA-Next - Image analysis
- Flux.1 - Image generation

### Cloud APIs
- Claude 3.5 Sonnet - Deep reasoning and writing
- OpenAI GPT-4 - Fallback option

## 🔑 **Configuration**

### API Keys (Optional)
Add in the Settings page:
- **Anthropic API Key** - For Claude models
- **OpenAI API Key** - For GPT models  
- **Hugging Face Token** - For HF models

### Local Models Setup
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull models
ollama pull llama3.2:70b
ollama pull deepseek-coder:33b
ollama pull llava:latest
```

## 📁 **Project Structure**

```
Ethos-AI/
├── frontend/                 # React UI (mobile responsive)
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
- **Mobile data stays on your network**

## 🆘 **Troubleshooting**

### Common Issues:
1. **Port 1420 or 8000 in use**: Kill existing processes or change ports
2. **Python dependencies**: Make sure you're in the backend directory when installing
3. **Node modules**: Run `npm install` in the frontend directory
4. **Mobile can't connect**: Check firewall and IP address
5. **AI models not working**: Use the mock backend (`simple_main.py`) for testing

### Mobile-Specific Issues:
1. **Can't access from phone**: Check computer IP and firewall
2. **Slow on mobile**: Reduce model size or use cloud APIs
3. **Touch not working**: Make sure you're using the web interface, not desktop app

### Getting Help:
- Check the console for error messages
- Make sure both backend and frontend are running
- Try the mock backend first to test the UI
- For mobile issues, check network connectivity

## 📄 **License**

MIT License - see LICENSE file for details.

---

**Note**: This is a local application that runs on your computer. You can access it from your phone by connecting to your computer's IP address. All data stays on your local network for privacy. 