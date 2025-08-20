#!/usr/bin/env python3
"""
Setup tunneling for mobile access anywhere
"""

import subprocess
import sys
import os
import time

def check_node_npm():
    """Check if Node.js and npm are installed"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        npm_result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        return result.returncode == 0 and npm_result.returncode == 0
    except:
        return False

def install_localtunnel():
    """Install localtunnel globally"""
    try:
        print("📦 Installing localtunnel...")
        result = subprocess.run(['npm', 'install', '-g', 'localtunnel'], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error installing localtunnel: {e}")
        return False

def start_tunnel(port=8001):
    """Start localtunnel"""
    try:
        print(f"🌐 Starting tunnel on port {port}...")
        print("⏳ This will take a moment...")
        
        # Start localtunnel
        result = subprocess.run(['lt', '--port', str(port)], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            # Parse the output to get the URL
            output = result.stdout
            for line in output.split('\n'):
                if 'https://' in line and '.loca.lt' in line:
                    url = line.strip()
                    return url
        
        return None
    except Exception as e:
        print(f"❌ Error starting tunnel: {e}")
        return None

def main():
    """Main function"""
    print("🌐 Setting up Mobile Access Anywhere")
    print("=" * 40)
    
    # Check Node.js
    if not check_node_npm():
        print("❌ Node.js and npm are required")
        print("📥 Download from: https://nodejs.org/")
        return
    
    print("✅ Node.js and npm found")
    
    # Install localtunnel
    if not install_localtunnel():
        print("❌ Failed to install localtunnel")
        return
    
    print("✅ localtunnel installed")
    
    # Instructions
    print("\n📋 Next Steps:")
    print("1. Start your embedded AI server:")
    print("   cd mobile_app")
    print("   python embedded_ai_server.py")
    print()
    print("2. In another terminal, start the tunnel:")
    print("   lt --port 8001")
    print()
    print("3. You'll get a public URL like:")
    print("   https://your-app.loca.lt")
    print()
    print("4. Use this URL on your Z Fold 4:")
    print("   - Works on cellular data")
    print("   - No WiFi required")
    print("   - Access from anywhere!")
    print()
    print("🎯 Alternative: Use ngrok for more features")
    print("   npm install -g ngrok")
    print("   ngrok http 8001")

if __name__ == "__main__":
    main()
