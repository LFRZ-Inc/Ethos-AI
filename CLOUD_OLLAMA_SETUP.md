# 🌐 Cloud Ethos AI + Local Ollama Setup Guide

## 🎯 Goal
Connect your cloud Ethos AI server to your local Ollama models so you can use real AI responses from anywhere!

## 📋 Prerequisites
- ✅ Ollama running locally with models
- ✅ Cloud server deployed on Railway
- ✅ ngrok or similar tunnel service

## 🚀 Setup Options

### Option 1: ngrok (Recommended)

1. **Install ngrok:**
   ```bash
   # Download from https://ngrok.com/
   # Or use winget on Windows:
   winget install ngrok
   ```

2. **Sign up and get auth token:**
   - Go to https://ngrok.com/
   - Create free account
   - Get your auth token

3. **Authenticate ngrok:**
   ```bash
   ngrok config add-authtoken YOUR_TOKEN_HERE
   ```

4. **Start tunnel:**
   ```bash
   ngrok http 11434
   ```

5. **Get public URL:**
   - Check ngrok dashboard at http://localhost:4040
   - Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

### Option 2: Cloudflare Tunnel

1. **Install cloudflared:**
   ```bash
   # Download from https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/
   ```

2. **Start tunnel:**
   ```bash
   cloudflared tunnel --url http://localhost:11434
   ```

### Option 3: Manual Setup

If you don't want to use tunnel services, you can:

1. **Deploy Ollama to Railway** (limited resources)
2. **Use a different cloud provider** with GPU support
3. **Set up a VPS** with Ollama installed

## 🔧 Configuration

Once you have your tunnel URL, update the backend:

1. **Update tunnel URL in code:**
   ```python
   # In backend/ollama_bridge.py
   self.ollama_url = "YOUR_TUNNEL_URL_HERE"
   ```

2. **Deploy to Railway:**
   ```bash
   git add .
   git commit -m "Update tunnel URL"
   git push
   ```

## 🧪 Testing

1. **Test local connection:**
   ```bash
   python test_local_ethos.py
   ```

2. **Test cloud server:**
   ```bash
   curl https://cooking-ethos-ai-production-6bfd.up.railway.app/api/models
   ```

3. **Test chat:**
   ```bash
   curl -X POST https://cooking-ethos-ai-production-6bfd.up.railway.app/api/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello!", "model_override": "ethos-light"}'
   ```

## 🎉 Success!

Once configured, your cloud server will:
- ✅ Use your real Ollama models (gpt-oss:20b, llama3.1:70b, etc.)
- ✅ Be accessible from anywhere
- ✅ Provide real AI responses instead of hardcoded ones
- ✅ Maintain privacy (your models, your data)

## 🔒 Security Notes

- Keep your tunnel URL private
- Consider using authentication
- Monitor usage and costs
- Use HTTPS when possible

## 🆘 Troubleshooting

### "Cannot connect to Ollama"
- Make sure Ollama is running: `ollama serve`
- Check tunnel is active
- Verify tunnel URL is correct

### "Model not available"
- Check model names match exactly
- Ensure model is downloaded: `ollama list`
- Try pulling model: `ollama pull model-name`

### "Cloud server not responding"
- Check Railway deployment status
- Verify code changes are deployed
- Check logs for errors
