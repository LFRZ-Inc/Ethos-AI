from http.server import BaseHTTPRequestHandler
import json
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from backend.models.orchestrator import ModelOrchestrator
from backend.memory.database import Database
from backend.config.config import Config

# Initialize components
config = Config()
db = Database()
orchestrator = ModelOrchestrator(config, db)

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/chat':
            try:
                # Get request body
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                request_data = json.loads(post_data.decode('utf-8'))
                
                # Extract message and conversation_id
                message = request_data.get('message', '')
                conversation_id = request_data.get('conversation_id')
                
                # Get response from orchestrator
                response = orchestrator.get_response(message, conversation_id)
                
                # Return response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()
                
                response_data = {
                    'response': response.content,
                    'conversation_id': response.conversation_id,
                    'model_used': response.model_used,
                    'tools_called': response.tools_called
                }
                
                self.wfile.write(json.dumps(response_data).encode())
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers() 