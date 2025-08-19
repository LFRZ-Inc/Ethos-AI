#!/usr/bin/env python3
"""
LocalTunnel Setup for Railway Testing
Exposes local FastAPI server to the internet via LocalTunnel
"""

import subprocess
import time
import requests
import json
import os
from datetime import datetime

def install_localtunnel():
    """Install LocalTunnel globally"""
    print("📦 Installing LocalTunnel...")
    try:
        result = subprocess.run(['npm', 'install', '-g', 'localtunnel'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ LocalTunnel installed successfully")
            return True
        else:
            print(f"❌ Failed to install LocalTunnel: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error installing LocalTunnel: {e}")
        return False

def start_localtunnel(port=8000, subdomain=None):
    """Start LocalTunnel to expose local server"""
    print(f"🚀 Starting LocalTunnel on port {port}...")
    
    cmd = ['lt', '--port', str(port)]
    if subdomain:
        cmd.extend(['--subdomain', subdomain])
    
    try:
        # Start LocalTunnel in background
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait for tunnel to establish
        time.sleep(5)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ LocalTunnel started successfully")
            print("🌐 Your local server is now accessible via LocalTunnel")
            print("📱 You can test it from your phone or other devices")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ LocalTunnel failed to start: {stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting LocalTunnel: {e}")
        return None

def test_tunnel_connection(tunnel_url):
    """Test if the tunnel is working"""
    try:
        response = requests.get(f"{tunnel_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Tunnel working! Server response: {data}")
            return True
        else:
            print(f"❌ Tunnel not working. Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing tunnel: {e}")
        return False

def main():
    """Main function to setup LocalTunnel"""
    print("🚀 Ethos AI - LocalTunnel Setup for Railway Testing")
    print("=" * 50)
    
    # Check if LocalTunnel is installed
    try:
        result = subprocess.run(['lt', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            print("📦 LocalTunnel not found, installing...")
            if not install_localtunnel():
                print("❌ Failed to install LocalTunnel")
                return
    except:
        print("📦 LocalTunnel not found, installing...")
        if not install_localtunnel():
            print("❌ Failed to install LocalTunnel")
            return
    
    # Get port from environment or use default
    port = int(os.getenv("PORT", 8000))
    
    # Start LocalTunnel
    process = start_localtunnel(port)
    if not process:
        print("❌ Failed to start LocalTunnel")
        return
    
    print("\n📋 Instructions:")
    print("1. Make sure your FastAPI server is running on port", port)
    print("2. LocalTunnel will provide a public URL")
    print("3. You can test the API from any device using that URL")
    print("4. Press Ctrl+C to stop the tunnel")
    
    try:
        # Keep the tunnel running
        while True:
            time.sleep(1)
            if process.poll() is not None:
                print("❌ LocalTunnel stopped unexpectedly")
                break
    except KeyboardInterrupt:
        print("\n🛑 Stopping LocalTunnel...")
        process.terminate()
        print("✅ LocalTunnel stopped")

if __name__ == "__main__":
    main()
