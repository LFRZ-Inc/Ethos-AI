#!/usr/bin/env python3
"""
Ethos AI - Local Network Server
This allows Ethos AI to be accessed from any device on the same network
No internet required - works completely offline
"""

import socket
import subprocess
import threading
import time
import os
import sys
from pathlib import Path

def get_local_ip():
    """Get the local IP address of this machine"""
    try:
        # Connect to a remote address to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

def start_local_server():
    """Start the FastAPI server on all network interfaces"""
    local_ip = get_local_ip()
    port = 8000
    
    print("🌐 Starting Ethos AI Local Network Server...")
    print(f"📱 Local IP: {local_ip}")
    print(f"🔗 Access URL: http://{local_ip}:{port}")
    print(f"📱 Mobile Access: http://{local_ip}:{port}")
    print("=" * 50)
    
    # Start the FastAPI server
    try:
        # Import and run the main FastAPI app
        from client_storage_version import app
        
        import uvicorn
        uvicorn.run(
            app,
            host="0.0.0.0",  # Listen on all interfaces
            port=port,
            reload=False,
            access_log=True
        )
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False

def create_mobile_qr():
    """Create a QR code for easy mobile access"""
    try:
        import qrcode
        local_ip = get_local_ip()
        url = f"http://{local_ip}:8000"
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(url)
        qr.make(fit=True)
        
        qr_image = qr.make_image(fill_color="black", back_color="white")
        qr_image.save("ethos_ai_mobile_qr.png")
        
        print(f"📱 QR Code saved as: ethos_ai_mobile_qr.png")
        print(f"📱 Scan with your phone to access Ethos AI!")
        
    except ImportError:
        print("📱 Install qrcode: pip install qrcode[pil]")
    except Exception as e:
        print(f"❌ Error creating QR code: {e}")

def main():
    """Main function"""
    print("🚀 Ethos AI - Local Network Server")
    print("=" * 50)
    
    # Create QR code for mobile access
    create_mobile_qr()
    
    # Start the server
    start_local_server()

if __name__ == "__main__":
    main()
