# 🖥️ Server Setup Guide for Ethos AI

## 🎯 **SIMPLE SERVER DEPLOYMENT**

### **Option 1: Your PC as Server (Easiest)**

#### **Step 1: Start Backend Server**
```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Start the server
python main.py
```

#### **Step 2: Start Frontend Server**
```bash
# Open new terminal, navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

#### **Step 3: Access from Anywhere**
- **PC**: http://localhost:1420
- **Phone**: http://YOUR_PC_IP:1420
- **Any device**: http://YOUR_PC_IP:1420

---

### **Option 2: Dedicated Server (Recommended)**

#### **Requirements:**
- **VPS/Cloud Server** (DigitalOcean, AWS, etc.)
- **Domain name** (optional)
- **SSL certificate** (optional)

#### **Step 1: Server Setup**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Python
sudo apt install python3 python3-pip -y

# Install PM2 (process manager)
sudo npm install -g pm2
```

#### **Step 2: Deploy Application**
```bash
# Clone your repository
git clone https://github.com/LFRZ-Inc/Ethos-AI.git
cd Ethos-AI

# Setup backend
cd backend
pip install -r requirements.txt

# Setup frontend
cd ../frontend
npm install
npm run build
```

#### **Step 3: Start Services**
```bash
# Start backend with PM2
cd backend
pm2 start main.py --name "ethos-backend" --interpreter python3

# Start frontend with PM2
cd ../frontend
pm2 serve dist 1420 --name "ethos-frontend" --spa

# Save PM2 configuration
pm2 save
pm2 startup
```

#### **Step 4: Configure Firewall**
```bash
# Allow HTTP and HTTPS
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 1420
sudo ufw allow 8003
```

---

### **Option 3: Docker Deployment (Advanced)**

#### **Create Dockerfile**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Copy application
COPY . .

# Install Python dependencies
RUN pip install -r backend/requirements.txt

# Install Node.js dependencies and build frontend
RUN cd frontend && npm install && npm run build

# Expose ports
EXPOSE 8003 1420

# Start services
CMD ["python", "backend/main.py"]
```

#### **Run with Docker**
```bash
# Build image
docker build -t ethos-ai .

# Run container
docker run -d -p 8003:8003 -p 1420:1420 --name ethos-ai ethos-ai
```

---

## 🌐 **MAKING IT ACCESSIBLE FROM ANYWHERE**

### **Option 1: Port Forwarding (Home Network)**
1. **Access your router** (192.168.1.1)
2. **Set up port forwarding** for port 1420
3. **Use your public IP** to access from anywhere

### **Option 2: ngrok (Temporary)**
```bash
# Install ngrok
npm install -g ngrok

# Expose your local server
ngrok http 1420

# Use the ngrok URL to access from anywhere
```

### **Option 3: Cloudflare Tunnel (Free)**
```bash
# Install cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# Create tunnel
cloudflared tunnel create ethos-ai

# Configure tunnel
cloudflared tunnel route dns ethos-ai your-domain.com

# Start tunnel
cloudflared tunnel run ethos-ai
```

---

## 🔧 **ENVIRONMENT VARIABLES**

### **Create .env file in backend:**
```env
# Database
DATABASE_URL=sqlite:///ethos_ai.db

# API Keys (optional)
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

# Server
HOST=0.0.0.0
PORT=8003
```

---

## 📱 **ACCESS FROM PHONE**

### **Local Network:**
- **Find your PC's IP**: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
- **Access from phone**: `http://YOUR_PC_IP:1420`

### **From Anywhere:**
- **Use ngrok URL** (temporary)
- **Use your domain** (permanent)
- **Use public IP** (if port forwarded)

---

## 🎉 **ADVANTAGES OF SERVER DEPLOYMENT**

- ✅ **Full control** over environment
- ✅ **No platform limitations**
- ✅ **Easier debugging**
- ✅ **More reliable**
- ✅ **Can customize everything**
- ✅ **No build issues**
- ✅ **Direct access to logs**

---

## 🚀 **QUICK START (Your PC)**

1. **Start backend**: `cd backend && python main.py`
2. **Start frontend**: `cd frontend && npm run dev`
3. **Access**: http://localhost:1420
4. **Phone access**: http://YOUR_PC_IP:1420

**This will work immediately without any deployment issues!** 🎉 