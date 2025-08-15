import os
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuration
OLLAMA_HOST = os.environ.get('OLLAMA_HOST', 'localhost')
OLLAMA_PORT = os.environ.get('OLLAMA_PORT', '11434')
ETHOS_API_URL = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}"

@app.route('/')
def home():
    """Home endpoint"""
    return jsonify({
        'message': 'Ethos AI API for Cooking With!',
        'status': 'running',
        'version': '1.0.0'
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Check if Ollama is running
        response = requests.get(f"{ETHOS_API_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            return jsonify({
                'status': 'healthy',
                'ollama_connected': True,
                'models': response.json().get('models', [])
            })
        else:
            return jsonify({
                'status': 'unhealthy',
                'ollama_connected': False,
                'error': 'Ollama not responding'
            }), 503
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'ollama_connected': False,
            'error': str(e)
        }), 503

@app.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint for Ethos AI"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        content = data.get('content', '')
        model_override = data.get('model_override', 'llama3.2-3b')
        use_tools = data.get('use_tools', False)
        
        if not content:
            return jsonify({'error': 'Content is required'}), 400
        
        # Prepare request for Ollama
        ollama_request = {
            'model': model_override,
            'prompt': content,
            'stream': False
        }
        
        # Make request to Ollama
        response = requests.post(
            f"{ETHOS_API_URL}/api/generate",
            json=ollama_request,
            timeout=120  # 2 minute timeout
        )
        
        if response.status_code != 200:
            return jsonify({
                'error': f'Ollama API error: {response.status_code}',
                'details': response.text
            }), 500
        
        ollama_response = response.json()
        
        return jsonify({
            'content': ollama_response.get('response', ''),
            'model_used': model_override,
            'usage': {
                'prompt_tokens': ollama_response.get('prompt_eval_count', 0),
                'completion_tokens': ollama_response.get('eval_count', 0),
                'total_tokens': ollama_response.get('prompt_eval_count', 0) + ollama_response.get('eval_count', 0)
            }
        })
        
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Request timeout'}), 408
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/models', methods=['GET'])
def list_models():
    """List available models"""
    try:
        response = requests.get(f"{ETHOS_API_URL}/api/tags", timeout=10)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': 'Failed to fetch models'}), 500
    except Exception as e:
        return jsonify({'error': f'Error fetching models: {str(e)}'}), 500

@app.route('/pull', methods=['POST'])
def pull_model():
    """Pull a model from Ollama"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        model_name = data.get('model')
        
        if not model_name:
            return jsonify({'error': 'Model name is required'}), 400
        
        # Start model pull
        response = requests.post(
            f"{ETHOS_API_URL}/api/pull",
            json={'name': model_name},
            timeout=300  # 5 minute timeout for model download
        )
        
        if response.status_code == 200:
            return jsonify({'message': f'Model {model_name} pulled successfully'})
        else:
            return jsonify({'error': f'Failed to pull model: {response.text}'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Error pulling model: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
