#!/usr/bin/env python3
"""
Get IP address for mobile access
"""

import socket
import subprocess
import platform

def get_local_ip():
    """Get the local IP address"""
    try:
        # Connect to a remote address to get local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        return local_ip
    except:
        return "127.0.0.1"

def get_windows_ip():
    """Get IP address on Windows"""
    try:
        result = subprocess.run(
            ['ipconfig'], 
            capture_output=True, 
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                if 'IPv4 Address' in line and '192.168' in line:
                    ip = line.split(':')[-1].strip()
                    return ip
    except:
        pass
    return get_local_ip()

def main():
    """Main function"""
    print("🌐 Getting IP Address for Mobile Access")
    print("=" * 40)
    
    # Get IP address
    if platform.system() == "Windows":
        ip = get_windows_ip()
    else:
        ip = get_local_ip()
    
    print(f"📱 Your laptop's IP address: {ip}")
    print(f"🔗 Mobile access URL: http://{ip}:8001")
    print()
    print("📋 Instructions for Z Fold 4:")
    print("1. Make sure your phone is on the same WiFi")
    print("2. Open browser on your phone")
    print(f"3. Go to: http://{ip}:8001")
    print("4. Tap menu → 'Add to Home screen'")
    print("5. Enjoy Ethos AI on your phone! 🎉")
    print()
    print("💡 Tip: If port 8001 doesn't work, try 8002, 8003, etc.")

if __name__ == "__main__":
    main()
