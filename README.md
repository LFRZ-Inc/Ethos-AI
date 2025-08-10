# Ethos AI - Local-First Hybrid AI Interface

A powerful, privacy-focused AI interface that runs entirely on your device, combining local models with cloud APIs for optimal performance.

## Features

- **Multi-Model Orchestration**: Intelligent routing between local and cloud models
- **Local-First Architecture**: All data stored locally, works offline
- **Multi-Modal Support**: Text, image, and audio processing
- **Vector Memory**: Persistent, searchable conversation history
- **Tool Calling**: Code execution, web search, file analysis
- **Cross-Platform**: Windows, macOS, and Linux support

## Models Supported

### Local Models (via Ollama/LM Studio)
- LLaMA 3 70B (quantized) - General chat
- DeepSeek-R1 - Math and logic
- CodeLLaMA - Programming assistance
- LLaVA-Next - Image analysis
- Flux.1 - Image generation

### Cloud APIs
- Claude 3.5 Sonnet - Deep reasoning and writing
- OpenAI GPT-4 - Fallback option

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Ollama (for local models)
- 16GB+ RAM recommended

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Ethos-AI
   ```

2. **Install Python dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Install frontend dependencies**
   ```bash
   cd ../frontend
   npm install
   ```

4. **Setup local models**
   ```bash
   # Install Ollama
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Pull required models
   ollama pull llama3.2:70b
   ollama pull deepseek-coder:33b
   ollama pull llava:latest
   ```

5. **Configure API keys**
   - Copy `backend/config/config.example.yaml` to `backend/config/config.yaml`
   - Add your API keys for Claude, OpenAI, etc.

6. **Start the application**
   ```bash
   # Terminal 1: Start backend
   cd backend
   python main.py
   
   # Terminal 2: Start frontend
   cd frontend
   npm run dev
   ```

## Project Structure

```
Ethos-AI/
├── frontend/                 # Tauri + React UI
├── backend/                  # Python orchestration
│   ├── models/              # Model connectors
│   ├── memory/              # Vector store & embeddings
│   ├── tools/               # Tool calling implementations
│   └── config/              # Configuration files
├── memory/                   # Local data storage
├── docs/                     # Documentation
└── scripts/                  # Build and deployment scripts
```

## Configuration

### Model Orchestration
Edit `backend/config/orchestration.yaml` to customize routing logic:

```yaml
routing:
  math_logic:
    - deepseek-r1
    - claude-3.5
  coding:
    - codellama
    - claude-3.5
  general_chat:
    - llama3-70b
    - claude-3.5
  image_analysis:
    - llava-next
  image_generation:
    - flux-1
```

### Adding New Models
1. Create model connector in `backend/models/`
2. Add configuration in `backend/config/models.yaml`
3. Update orchestration rules

## Data Storage

All data is stored locally in `~/EthosAIData/`:
- `conversations/` - Chat history
- `embeddings/` - Vector database
- `models/` - Downloaded models
- `config/` - User preferences

## Building for Distribution

### Windows
```bash
cd frontend
npm run tauri build
```

### macOS
```bash
cd frontend
npm run tauri build
```

### Linux
```bash
cd frontend
npm run tauri build
```

## Offline Mode

Ethos AI works completely offline once local models are downloaded:
- All conversations stored locally
- Vector search works without internet
- Local models handle all requests
- Graceful fallback when cloud APIs unavailable

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details. 