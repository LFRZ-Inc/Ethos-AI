#!/usr/bin/env python3
"""
Ethos AI - Embedded AI Server
Runs on any device (mobile, tablet, laptop) as a local AI server
No cloud required - completely self-contained
"""

import os
import sys
import threading
import time
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
import platform

class EmbeddedAIServer:
    """Embedded AI server that runs on any device"""
    
    def __init__(self, device_type: str = "mobile"):
        self.device_type = device_type
        self.server_running = False
        self.models_available = []
        self.device_specs = self.get_device_specs()
        self.port = self.get_available_port()
        
    def get_device_specs(self) -> Dict:
        """Get device specifications to determine AI capabilities"""
        specs = {
            "platform": platform.system(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "memory": self.get_memory_info(),
            "storage": self.get_storage_info(),
            "device_type": self.device_type
        }
        return specs
    
    def get_memory_info(self) -> Dict:
        """Get available memory information"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            return {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "percent_used": memory.percent
            }
        except:
            return {"total_gb": 4, "available_gb": 2, "percent_used": 50}
    
    def get_storage_info(self) -> Dict:
        """Get available storage information"""
        try:
            import psutil
            disk = psutil.disk_usage('/')
            return {
                "total_gb": round(disk.total / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "percent_used": round((disk.used / disk.total) * 100, 2)
            }
        except:
            return {"total_gb": 64, "free_gb": 32, "percent_used": 50}
    
    def get_available_port(self) -> int:
        """Find an available port for the server"""
        import socket
        for port in range(8000, 8020):  # Check more ports
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    s.close()  # Close the test socket
                    return port
            except OSError:
                continue
        return 8000
    
    def select_models_for_device(self) -> List[Dict]:
        """Select appropriate AI models based on device specs"""
        memory_gb = self.device_specs["memory"]["available_gb"]
        storage_gb = self.device_specs["storage"]["free_gb"]
        
        models = []
        
        # Lightweight models for mobile devices
        if memory_gb >= 2 and storage_gb >= 2:
            models.append({
                "name": "phi:1b",
                "size_gb": 1.6,
                "type": "text_generation",
                "priority": 1
            })
        
        if memory_gb >= 4 and storage_gb >= 4:
            models.append({
                "name": "llama2:1b", 
                "size_gb": 1.1,
                "type": "text_generation",
                "priority": 2
            })
        
        if memory_gb >= 6 and storage_gb >= 6:
            models.append({
                "name": "llama3.2:3b",
                "size_gb": 3.4,
                "type": "text_generation", 
                "priority": 3
            })
        
        if memory_gb >= 10 and storage_gb >= 10:
            models.append({
                "name": "codellama:7b",
                "size_gb": 7.2,
                "type": "code_generation",
                "priority": 4
            })
        
        return models
    
    def download_models(self) -> bool:
        """Download AI models based on device capabilities"""
        models = self.select_models_for_device()
        
        if not models:
            print("❌ Device doesn't meet minimum requirements")
            return False
        
        print(f"📱 Device specs: {self.device_specs['memory']['available_gb']}GB RAM, {self.device_specs['storage']['free_gb']}GB storage")
        print(f"🤖 Selected models: {[m['name'] for m in models]}")
        
        # Check if Ollama is available
        if not self.check_ollama():
            print("❌ Ollama not available - installing...")
            if not self.install_ollama():
                return False
        
        # Download models
        for model in models:
            if not self.download_model(model["name"]):
                print(f"⚠️ Failed to download {model['name']}, skipping...")
                continue
            self.models_available.append(model)
        
        return len(self.models_available) > 0
    
    def check_ollama(self) -> bool:
        """Check if Ollama is installed and available"""
        try:
            result = subprocess.run(
                ['ollama', '--version'], 
                capture_output=True, 
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            return result.returncode == 0
        except:
            return False
    
    def install_ollama(self) -> bool:
        """Install Ollama on the device"""
        try:
            if platform.system() == "Windows":
                # Windows installation
                subprocess.run(['winget', 'install', 'ollama'], check=True)
            elif platform.system() == "Darwin":
                # macOS installation
                subprocess.run(['brew', 'install', 'ollama'], check=True)
            else:
                # Linux installation
                subprocess.run(['curl', '-fsSL', 'https://ollama.ai/install.sh', '|', 'sh'], 
                             shell=True, check=True)
            return True
        except:
            print("❌ Failed to install Ollama automatically")
            print("📱 Please install Ollama manually: https://ollama.ai")
            return False
    
    def download_model(self, model_name: str) -> bool:
        """Download a specific AI model"""
        try:
            print(f"📥 Downloading {model_name}...")
            # Fix Windows encoding issue
            result = subprocess.run(
                ['ollama', 'pull', model_name], 
                capture_output=True, 
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            return result.returncode == 0
        except Exception as e:
            print(f"❌ Error downloading {model_name}: {e}")
            return False
    
    def start_server(self) -> bool:
        """Start the embedded AI server"""
        if not self.models_available:
            print("❌ No models available - run download_models() first")
            return False
        
        print(f"🚀 Starting embedded AI server on port {self.port}...")
        print(f"📱 Device: {self.device_type}")
        print(f"🤖 Models: {[m['name'] for m in self.models_available]}")
        
        # Start server in background thread
        server_thread = threading.Thread(target=self._run_server)
        server_thread.daemon = True
        server_thread.start()
        
        self.server_running = True
        return True
    
    def _run_server(self):
        """Run the FastAPI server"""
        try:
            # Add parent directory to path to find the module
            import sys
            import os
            parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            backend_dir = os.path.join(parent_dir, 'backend')
            sys.path.insert(0, backend_dir)
            
            # Import and run the server
            from client_storage_version import app
            import uvicorn
            
            uvicorn.run(
                app,
                host="0.0.0.0",
                port=self.port,
                reload=False,
                access_log=False
            )
        except Exception as e:
            print(f"❌ Server error: {e}")
            print(f"📁 Current directory: {os.getcwd()}")
            print(f"📁 Backend directory: {backend_dir}")
            self.server_running = False
    
    def get_server_info(self) -> Dict:
        """Get server information"""
        return {
            "running": self.server_running,
            "port": self.port,
            "device_specs": self.device_specs,
            "models_available": self.models_available,
            "url": f"http://localhost:{self.port}" if self.server_running else None
        }
    
    def stop_server(self):
        """Stop the embedded server"""
        self.server_running = False
        print("🛑 Server stopped")

def main():
    """Main function for embedded AI server"""
    print("🚀 Ethos AI - Embedded AI Server")
    print("=" * 50)
    
    # Create embedded server
    server = EmbeddedAIServer()
    
    # Download models
    if not server.download_models():
        print("❌ Failed to prepare models")
        return
    
    # Start server
    if server.start_server():
        info = server.get_server_info()
        print(f"✅ Server running at: {info['url']}")
        print("📱 Access from any device on the same network!")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            server.stop_server()

if __name__ == "__main__":
    main()
