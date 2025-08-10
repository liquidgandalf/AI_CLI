# AI Chat Interface

A minimal web-based chat interface for local AI models using Ollama.

## Features

- 🤖 Direct chat with local AI models (currently using gemma3:12b)
- 🌐 Clean, modern web interface
- ⚡ Real-time messaging with loading states
- 📱 Mobile-responsive design
- 🔧 Easy to extend for additional workflows

## Quick Start

1. **Ensure Ollama is running:**
   ```bash
   ollama serve
   ```

2. **Start the chat interface:**
   ```bash
   source venv/bin/activate
   python app.py
   ```

3. **Open your browser:**
   Navigate to `http://localhost:5785`

## Available Models

Current models available in your Ollama installation:
- gemma3:12b (8.1 GB) - Currently active
- deepseek-r1:14b (9.0 GB)
- deepseek-r1:1.5b (1.1 GB)
- mistral:latest (4.1 GB)
- llama3:8b (4.7 GB)

## API Endpoints

- `GET /` - Main chat interface
- `POST /api/chat` - Send message to AI
- `GET /api/models` - List available models

## Next Steps

This is Phase 1 of the larger project. Future phases will include:
- Database interrogation workflows
- Part number processing automation
- Advanced workflow management
- Multi-model support

## Requirements

- Python 3.8+
- Ollama with at least one model installed
- Flask and requests (see requirements.txt)
