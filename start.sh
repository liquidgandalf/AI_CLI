#!/bin/bash

# AI Chat Interface Startup Script
# This script starts the complete AI chat system with all dependencies

echo "🚀 Starting AI Chat Interface..."
echo "================================"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found. Make sure you're running this from the AI_CLI directory."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Error: Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Error: Ollama is not installed. Please install Ollama first."
    echo "   Visit: https://ollama.ai"
    exit 1
fi

# Check if Ollama service is running
echo "🤖 Checking Ollama service..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  Ollama service not running. Starting Ollama..."
    ollama serve &
    OLLAMA_PID=$!
    
    # Wait for Ollama to start
    echo "   Waiting for Ollama to start..."
    for i in {1..30}; do
        if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
            echo "✅ Ollama service started successfully!"
            break
        fi
        sleep 1
        if [ $i -eq 30 ]; then
            echo "❌ Error: Ollama failed to start within 30 seconds"
            exit 1
        fi
    done
else
    echo "✅ Ollama service is already running"
fi

# Check if required model is available
echo "🧠 Checking AI model availability..."
if ollama list | grep -q "gpt-oss:20b"; then
    echo "✅ gpt-oss:20b model is available"
else
    echo "⚠️  gpt-oss:20b model not found. Downloading..."
    ollama pull gpt-oss:20b
    if [ $? -eq 0 ]; then
        echo "✅ gpt-oss:20b model downloaded successfully"
    else
        echo "❌ Error: Failed to download gpt-oss:20b model"
        exit 1
    fi
fi

# Initialize database if needed
echo "🗄️  Initializing database..."
python database.py

# Check if initialization was successful
if [ $? -eq 0 ]; then
    echo "✅ Database initialized successfully"
else
    echo "❌ Error: Database initialization failed"
    exit 1
fi

# Start the background file processing worker
echo "🔧 Starting background file processing worker..."
python process_unprocessed_files.py --loop &
WORKER_PID=$!
echo "✅ Background worker started (PID: $WORKER_PID)"

# Start the application
echo "🌐 Starting AI Chat Interface on http://localhost:5785..."
echo "================================"
echo "📝 Access the web interface at: http://localhost:5785"
echo "🔑 Create an account or login to start chatting"
echo "🔧 Background worker is processing files automatically"
echo "🛑 Press Ctrl+C to stop both server and worker"
echo "================================"

# Start the Flask application
python app.py

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Shutting down AI Chat Interface..."
    if [ ! -z "$WORKER_PID" ]; then
        echo "   Stopping background worker..."
        kill $WORKER_PID 2>/dev/null
    fi
    if [ ! -z "$OLLAMA_PID" ]; then
        echo "   Stopping Ollama service..."
        kill $OLLAMA_PID 2>/dev/null
    fi
    echo "✅ Shutdown complete"
}

# Set up signal handlers for graceful shutdown
trap cleanup EXIT INT TERM
