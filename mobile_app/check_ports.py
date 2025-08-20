#!/usr/bin/env python3
"""
Check what's using port 8000
"""

import subprocess
import sys

def check_port_usage(port=8000):
    """Check what process is using a specific port"""
    try:
        # Windows command to check port usage
        result = subprocess.run(
            ['netstat', '-ano'], 
            capture_output=True, 
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                if f':{port}' in line and 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        print(f"🔍 Port {port} is being used by PID: {pid}")
                        
                        # Get process name
                        try:
                            task_result = subprocess.run(
                                ['tasklist', '/FI', f'PID eq {pid}'], 
                                capture_output=True, 
                                text=True,
                                encoding='utf-8',
                                errors='ignore'
                            )
                            if task_result.returncode == 0:
                                task_lines = task_result.stdout.split('\n')
                                for task_line in task_lines:
                                    if pid in task_line:
                                        print(f"📋 Process: {task_line}")
                                        break
                        except:
                            pass
                        return True
            
            print(f"✅ Port {port} is available")
            return False
        else:
            print(f"❌ Error checking port {port}")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return True

def find_available_port(start_port=8000, max_attempts=20):
    """Find an available port starting from start_port"""
    import socket
    
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                s.close()
                print(f"✅ Port {port} is available")
                return port
        except OSError:
            print(f"❌ Port {port} is in use")
            continue
    
    print(f"❌ No available ports found in range {start_port}-{start_port + max_attempts}")
    return None

if __name__ == "__main__":
    print("🔍 Checking Port Usage")
    print("=" * 30)
    
    # Check port 8000 specifically
    print(f"Checking port 8000...")
    port_8000_in_use = check_port_usage(8000)
    
    print("\n🔍 Finding available port...")
    available_port = find_available_port(8000, 20)
    
    if available_port:
        print(f"\n✅ Use port {available_port} for your server")
    else:
        print("\n❌ No available ports found")
