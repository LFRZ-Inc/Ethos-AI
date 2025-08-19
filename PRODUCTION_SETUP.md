# ETHOS AI - PRODUCTION SETUP GUIDE

## 🚀 Quick Start (Windows)

### Option 1: Automated Startup
```bash
# Double-click or run:
start_production.bat
```

### Option 2: Manual Startup
```bash
# 1. Start Backend
cd backend
python client_storage_version.py

# 2. Start Frontend (new terminal)
cd frontend
npm run dev

# 3. Start LocalTunnel (new terminal)
lt --port 8000 --subdomain ethos-ai-test
```

## 📋 Prerequisites

### Required Software:
1. **Python 3.8+** - [Download](https://python.org)
2. **Node.js 16+** - [Download](https://nodejs.org)
3. **Ollama** - [Download](https://ollama.ai)
4. **LocalTunnel** - Install with: `npm install -g localtunnel`

### Required AI Models:
```bash
# Download these models with Ollama:
ollama pull sailor2:1b
ollama pull codellama:7b
ollama pull llama3.2:3b
```

## 🔧 Installation Steps

### 1. Install Dependencies
```bash
# Backend dependencies
cd backend
pip install fastapi uvicorn python-multipart

# Frontend dependencies
cd frontend
npm install
```

### 2. Verify Ollama Installation
```bash
ollama --version
ollama list
```

### 3. Test Backend
```bash
cd backend
python client_storage_version.py
# Should show: "✅ Ollama is available - Real AI models will be used"
```

### 4. Test Frontend
```bash
cd frontend
npm run dev
# Should show: "Local: http://localhost:1420/"
```

## 🌐 Access URLs

### Local Development:
- **Frontend**: http://localhost:1420
- **Backend**: http://127.0.0.1:8000
- **Health Check**: http://127.0.0.1:8000/health

### Remote Access (via LocalTunnel):
- **Backend API**: https://ethos-ai-test.loca.lt
- **Mobile/Remote**: Use this URL from any device

## 🛠️ Production Features

### ✅ Real AI Models:
- **sailor2:1b** - General purpose, multilingual
- **codellama:7b** - Advanced coding
- **llama3.2:3b** - Quality analysis
- **Smart Selection** - Automatically picks best model

### ✅ Client-Side Storage:
- **Privacy First** - No server storage
- **Device Memory** - Conversations stored locally
- **Cross-Device** - Works on phone, tablet, desktop
- **Offline Capable** - Works without internet

### ✅ Production APIs:
- **Real File Upload** - Process text files
- **Health Monitoring** - System status
- **Model Status** - Available models
- **Error Handling** - Proper HTTP errors

## 🔍 Troubleshooting

### Backend Issues:
```bash
# Check if Ollama is running
ollama list

# Check if models are downloaded
ollama list | grep sailor2

# Restart backend
taskkill /f /im python.exe
cd backend
python client_storage_version.py
```

### Frontend Issues:
```bash
# Check if Node.js is running
netstat -ano | findstr :1420

# Restart frontend
taskkill /f /im node.exe
cd frontend
npm run dev
```

### LocalTunnel Issues:
```bash
# Check if tunnel is working
curl https://ethos-ai-test.loca.lt/health

# Restart tunnel
taskkill /f /im node.exe
lt --port 8000 --subdomain ethos-ai-test
```

## 📊 System Requirements

### Minimum:
- **RAM**: 8GB (for 1B models)
- **Storage**: 10GB free space
- **CPU**: 4 cores

### Recommended:
- **RAM**: 16GB+ (for 7B models)
- **Storage**: 20GB+ free space
- **CPU**: 8 cores+

## 🔒 Security & Privacy

### Privacy Features:
- ✅ No server-side conversation storage
- ✅ Client manages all data
- ✅ Local AI processing
- ✅ No tracking or analytics

### Security Features:
- ✅ CORS enabled for local development
- ✅ Input validation
- ✅ Error handling
- ✅ File upload restrictions

## 📱 Mobile/Remote Usage

### From Phone:
1. Start LocalTunnel: `lt --port 8000 --subdomain ethos-ai-test`
2. Use URL: `https://ethos-ai-test.loca.lt`
3. Chat with AI from your phone

### From Other Devices:
1. Ensure LocalTunnel is running
2. Access via the tunnel URL
3. All conversations stay on your device

## 🎯 Production Checklist

- [ ] Ollama installed and running
- [ ] Required models downloaded
- [ ] Backend starts without errors
- [ ] Frontend accessible at localhost:1420
- [ ] LocalTunnel working
- [ ] AI responses working
- [ ] File upload working
- [ ] No mock data in responses

## 🚨 Emergency Stop

```bash
# Stop all services:
stop_production.bat

# Or manually:
taskkill /f /im python.exe
taskkill /f /im node.exe
```

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section
2. Verify all prerequisites are installed
3. Ensure Ollama models are downloaded
4. Check system resources (RAM/CPU)

---

**Ethos AI Production v5.3.0** - Ready for real-world use! 🚀
