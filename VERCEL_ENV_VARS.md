# 🔧 Vercel Environment Variables Guide

## 📋 **REQUIRED ENVIRONMENT VARIABLES**

### **🎯 ESSENTIAL (For Basic Functionality)**

#### **1. API Keys (Optional - Only if you want cloud models)**
```env
# OpenAI API Key (for GPT models)
OPENAI_API_KEY=sk-your-openai-api-key-here

# Anthropic API Key (for Claude models)  
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key-here

# Google API Key (for Gemini models)
GOOGLE_API_KEY=your-google-api-key-here
```

#### **2. Database Configuration**
```env
# SQLite Database Path (Vercel will handle this automatically)
DATABASE_URL=sqlite:///ethos_ai.db

# Alternative: Use Vercel's built-in database
# DATABASE_URL=postgresql://user:pass@host:port/db
```

#### **3. Server Configuration**
```env
# Server Host (Vercel handles this)
HOST=0.0.0.0

# Server Port (Vercel handles this)
PORT=8003

# Environment
NODE_ENV=production
```

## 🔧 **OPTIONAL ENVIRONMENT VARIABLES**

### **🤖 AI Model Configuration**

#### **Ollama Configuration (Local Models)**
```env
# Ollama Base URL (if using external Ollama server)
OLLAMA_BASE_URL=http://localhost:11434

# Ollama API Key (if required)
OLLAMA_API_KEY=your-ollama-api-key
```

#### **Advanced Model Settings**
```env
# Default Model
DEFAULT_MODEL=llama3.2-3b

# Model Temperature
MODEL_TEMPERATURE=0.7

# Max Tokens
MAX_TOKENS=4096
```

### **🧠 Memory & Search Configuration**
```env
# Vector Store Type
VECTOR_STORE=chromadb

# Embedding Model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Max Memory Size
MAX_MEMORY_SIZE=10000

# Similarity Threshold
SIMILARITY_THRESHOLD=0.7
```

### **🔧 Tool Configuration**
```env
# Enable Python Execution
ENABLE_PYTHON_EXECUTION=true

# Enable Web Search
ENABLE_WEB_SEARCH=true

# Enable File Search
ENABLE_FILE_SEARCH=true

# Enable Code Execution
ENABLE_CODE_EXECUTION=true

# Sandbox Mode
SANDBOX_MODE=true
```

### **🎨 UI Configuration**
```env
# Default Theme
DEFAULT_THEME=dark

# Language
LANGUAGE=en

# Auto Save
AUTO_SAVE=true

# Max Conversations
MAX_CONVERSATIONS=100
```

## 🚀 **VERCEL-SPECIFIC VARIABLES**

### **Frontend Configuration**
```env
# API Base URL (Vercel will set this automatically)
VITE_API_BASE_URL=https://your-app.vercel.app

# Environment
VITE_NODE_ENV=production
```

### **Build Configuration**
```env
# Python Version
PYTHON_VERSION=3.11.0

# Node Version
NODE_VERSION=18
```

## 📝 **HOW TO SET IN VERCEL**

### **Step 1: Go to Vercel Dashboard**
1. **Open your project** in Vercel dashboard
2. **Click "Settings"** tab
3. **Click "Environment Variables"** in the left sidebar

### **Step 2: Add Variables**
For each environment variable:
1. **Name**: Enter the variable name (e.g., `OPENAI_API_KEY`)
2. **Value**: Enter the value (e.g., `sk-your-key-here`)
3. **Environment**: Select `Production` (and `Preview` if needed)
4. **Click "Add"**

### **Step 3: Redeploy**
After adding variables:
1. **Go to "Deployments"** tab
2. **Click "Redeploy"** on your latest deployment

## 🎯 **MINIMAL SETUP (RECOMMENDED)**

For basic functionality, you only need:

```env
# Optional: Only if you want cloud AI models
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Optional: Customize behavior
DEFAULT_MODEL=llama3.2-3b
DEFAULT_THEME=dark
```

## 🔒 **SECURITY NOTES**

### **✅ Safe to Commit:**
- `DEFAULT_MODEL`
- `DEFAULT_THEME`
- `LANGUAGE`
- `MAX_CONVERSATIONS`

### **❌ NEVER Commit:**
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GOOGLE_API_KEY`
- Any API keys or secrets

### **🔐 Best Practices:**
1. **Use Vercel's environment variables** (not .env files)
2. **Rotate API keys** regularly
3. **Use least privilege** for API keys
4. **Monitor usage** to avoid charges

## 🎉 **QUICK START**

### **For Local Models Only (Free):**
```env
# No environment variables needed!
# Ethos AI will work with local Ollama models
```

### **For Cloud Models (Paid):**
```env
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### **For Full Features:**
```env
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
DEFAULT_MODEL=llama3.2-3b
DEFAULT_THEME=dark
ENABLE_WEB_SEARCH=true
```

## 🆘 **TROUBLESHOOTING**

### **Common Issues:**
1. **"API key not found"** - Check environment variable name
2. **"Model not available"** - Verify model is enabled in config
3. **"Database error"** - Vercel handles this automatically
4. **"CORS error"** - Check API base URL configuration

### **Testing Environment Variables:**
Add this to your API function to debug:
```python
import os
print("Environment variables:", os.environ)
```

**Your Ethos AI will work with or without environment variables!** 🚀 