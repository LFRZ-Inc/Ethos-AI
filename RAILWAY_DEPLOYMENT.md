# Railway Deployment Guide for Cooking With! Integration

This simplified version of Ethos AI is designed to work with your Cooking With! app on Railway.

## 🚀 Quick Setup

### 1. Railway Deployment

The repository is already configured for Railway deployment. Railway will automatically:

- Detect the Python application
- Install dependencies from `requirements.txt`
- Start the Flask app using the `Procfile`
- Use Python 3.11 as specified in `runtime.txt`

### 2. Environment Variables

Add these environment variables in your Railway project:

```env
OLLAMA_HOST=0.0.0.0
OLLAMA_PORT=11434
PORT=8000
```

### 3. Pull Required Models

After deployment, pull the required models:

```bash
# Pull LLaVA model for image analysis
curl -X POST https://your-app.railway.app/pull \
  -H "Content-Type: application/json" \
  -d '{"model": "llava:7b"}'

# Pull Llama model for text generation
curl -X POST https://your-app.railway.app/pull \
  -H "Content-Type: application/json" \
  -d '{"model": "llama3.2:3b"}'
```

### 4. Configure Your Cooking With! App

Add to your Vercel environment variables:

```env
ETHOS_AI_URL=https://your-app.railway.app
```

## 🔧 API Endpoints

- `GET /health` - Health check
- `POST /chat` - Main chat endpoint
- `GET /models` - List available models
- `POST /pull` - Pull a model

## 📝 Usage Example

```typescript
// In your Cooking With! app
const response = await fetch('https://your-app.railway.app/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    content: 'Analyze this food image...',
    model_override: 'llava-7b'
  })
})
```

## 🎯 What This Provides

- **Simplified Flask API** - Easy to deploy and maintain
- **Ollama Integration** - Local AI models without API costs
- **CORS Enabled** - Works with your Vercel frontend
- **Health Monitoring** - Easy to check deployment status
- **Model Management** - Pull models via API

## 🔍 Troubleshooting

### Common Issues:

1. **Deployment fails**: Check Railway logs for Python version or dependency issues
2. **Models not found**: Use the `/pull` endpoint to download models
3. **Connection errors**: Verify environment variables are set correctly
4. **Timeout issues**: Increase timeout values in your Cooking With! app

### Debug Commands:

```bash
# Check health
curl https://your-app.railway.app/health

# List models
curl https://your-app.railway.app/models

# Test chat endpoint
curl -X POST https://your-app.railway.app/chat \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello", "model_override": "llama3.2-3b"}'
```

## 💰 Cost Optimization

- **Free tier**: 500 hours/month on Railway
- **Paid tier**: $5/month for 1000 hours
- **GPU tier**: $20/month for better performance

## 🎉 Success!

Once deployed, your Cooking With! app will have:
- ✅ Free AI food recognition
- ✅ No per-image costs
- ✅ Privacy (data stays on your infrastructure)
- ✅ Reliable cloud deployment
