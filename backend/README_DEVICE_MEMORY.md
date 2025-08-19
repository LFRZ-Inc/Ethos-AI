# Ethos AI - Multi-Model System with Device Memory

## 🚀 Overview

Ethos AI now features a revolutionary **device-local memory system** that allows each device to maintain its own conversation history while enabling optional device linking for shared context.

## 🧠 Key Features

### 📱 **Device Memory System**
- **Device Isolation**: Each device (phone, laptop, tablet) has its own private memory
- **No Server Storage**: All memory stays on the device, no database required
- **AI Context Access**: Models can read device memory for better responses
- **Persistent Memory**: Conversations persist across sessions

### 🔗 **Device Linking API**
- **Optional Linking**: Devices can be linked for shared context
- **Bidirectional**: Both devices can access each other's recent conversations
- **Privacy First**: Default isolation, opt-in sharing
- **Easy Management**: Link/unlink devices via simple API calls

### 🤖 **Smart Model Selection**
- **5 Models Available**: phi:1b, sailor2:1b, llama2:1b, llama3.2:3b, codellama:7b
- **Intelligent Selection**: Automatically chooses best model for each task
- **Task-Based**: Coding tasks → 7B/3B models, simple tasks → 1B models
- **Resource Efficient**: Loads/unloads models to save Railway memory

## 📋 API Endpoints

### Chat with Device Memory
```http
POST /api/chat
Content-Type: application/json

{
  "message": "Hello! Can you remember our previous conversations?",
  "device_id": "my-phone-123",
  "model_override": "ethos-phi",  // Optional
  "conversation_id": "conv_123"   // Optional
}
```

**Response:**
```json
{
  "response": "Yes! I remember our previous conversations...",
  "model": "ethos-phi",
  "device_id": "my-phone-123",
  "conversation_id": "conv_123",
  "deployment": "device-memory-system",
  "context_used": true
}
```

### Device Memory Retrieval
```http
GET /api/device/{device_id}/memory?limit=20
```

**Response:**
```json
{
  "device_id": "my-phone-123",
  "conversations": [
    {
      "id": "conv_123",
      "timestamp": "2024-01-01T12:00:00",
      "message": "Hello!",
      "response": "Hi there!",
      "model": "ethos-phi"
    }
  ],
  "total_conversations": 15,
  "deployment": "device-memory-system"
}
```

### Link Devices
```http
POST /api/device/link
Content-Type: application/json

{
  "device_id": "my-phone-123",
  "target_device_id": "my-laptop-456"
}
```

### Unlink Devices
```http
DELETE /api/device/link
Content-Type: application/json

{
  "device_id": "my-phone-123",
  "target_device_id": "my-laptop-456"
}
```

### Get Linked Devices
```http
GET /api/device/{device_id}/links
```

## 🚀 Quick Start

### 1. Start the Server
```bash
cd backend
python main.py
```

### 2. Test Device Memory
```bash
python test_device_memory.py
```

### 3. Use LocalTunnel for Railway Testing
```bash
python localtunnel_setup.py
```

## 📱 Usage Examples

### Example 1: Phone Conversation
```python
import requests

# First conversation on phone
response1 = requests.post("http://localhost:8000/api/chat", json={
    "message": "Hello! I'm using my phone.",
    "device_id": "my-phone-123"
})

# Second conversation (AI remembers the first)
response2 = requests.post("http://localhost:8000/api/chat", json={
    "message": "Do you remember what I said before?",
    "device_id": "my-phone-123"
})
```

### Example 2: Device Linking
```python
# Link phone and laptop
requests.post("http://localhost:8000/api/device/link", json={
    "device_id": "my-phone-123",
    "target_device_id": "my-laptop-456"
})

# Now AI can see conversations from both devices
response = requests.post("http://localhost:8000/api/chat", json={
    "message": "Can you see my laptop conversations?",
    "device_id": "my-phone-123"
})
```

### Example 3: Smart Model Selection
```python
# Coding task - automatically selects 7B or 3B model
response = requests.post("http://localhost:8000/api/chat", json={
    "message": "Write a Python function to sort a list",
    "device_id": "my-laptop-456"
})

# Simple task - automatically selects 1B model
response = requests.post("http://localhost:8000/api/chat", json={
    "message": "Hello! How are you?",
    "device_id": "my-laptop-456"
})
```

## 🤖 Available Models

| Model ID | Name | Size | Best For | Priority |
|----------|------|------|----------|----------|
| `ethos-phi` | Ethos Phi (1B) | 1.1 GB | Coding, Programming | 1 |
| `ethos-sailor` | Ethos Sailor (1B) | 1.1 GB | General, Multilingual | 2 |
| `ethos-fast` | Ethos Fast (1B) | 1.2 GB | Quick, Simple | 3 |
| `ethos-light` | Ethos Light (3B) | 3.4 GB | Quality, Analysis | 4 |
| `ethos-code` | Ethos Code (7B) | 7.2 GB | Advanced Coding | 5 |

## 🔧 Configuration

### Environment Variables
```bash
PORT=8000  # Server port
```

### Model Selection Keywords
- **Coding**: code, program, function, bug, error, python, javascript, etc.
- **Complex**: analyze, explain, compare, evaluate, design, architecture, etc.
- **Simple**: hello, hi, thanks, ok, yes, no, quick, simple, etc.

## 🧠 How Device Memory Works

1. **Device Identification**: Each request includes a `device_id`
2. **Memory Storage**: Conversations stored in device-specific memory
3. **Context Building**: AI receives recent conversation context
4. **Linked Context**: If devices are linked, AI gets context from both
5. **Memory Limits**: Keeps last 50 conversations, 100 messages for context

## 🔗 Device Linking Process

1. **Default Isolation**: Devices start isolated
2. **Optional Linking**: Use API to link devices
3. **Shared Context**: Linked devices share recent conversation context
4. **Bidirectional**: Both devices can access each other's context
5. **Easy Unlinking**: Remove links anytime

## 🚀 Railway Deployment

### Using LocalTunnel
1. Start your local server: `python main.py`
2. Run LocalTunnel: `python localtunnel_setup.py`
3. Use the provided URL to test from any device
4. Test device memory and linking features

### Direct Railway Deployment
1. Push code to GitHub
2. Deploy to Railway
3. Use Railway's domain for testing

## 📊 Testing

Run the comprehensive test suite:
```bash
python test_device_memory.py
```

This will test:
- ✅ Device memory isolation
- ✅ Device linking functionality
- ✅ Memory retrieval
- ✅ Smart model selection
- ✅ Context awareness

## 🎯 Benefits

### For Users
- **Privacy**: Device conversations stay private by default
- **Convenience**: Optional device linking for seamless experience
- **Context**: AI remembers conversations for better responses
- **Flexibility**: Link/unlink devices as needed

### For Developers
- **No Database**: No server-side storage required
- **Scalable**: Memory scales with device usage
- **Efficient**: Smart model selection saves resources
- **Flexible**: Easy to extend and customize

## 🔮 Future Enhancements

- **File-based Memory**: Persistent storage to disk
- **Memory Encryption**: Encrypt device memory
- **Memory Export**: Export/import device memory
- **Advanced Linking**: Multi-device linking groups
- **Memory Analytics**: Usage statistics and insights

---

**🎉 Enjoy your personalized, device-aware AI experience!**
