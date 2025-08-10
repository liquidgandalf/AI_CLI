#!/bin/bash

# AI Chat Interface Setup Script
# This script sets up the complete environment for the AI chat system

echo "🛠️  AI Chat Interface Setup"
echo "============================"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found. Make sure you're running this from the AI_CLI directory."
    exit 1
fi

# Check Python version
echo "🐍 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
if [ $? -eq 0 ]; then
    echo "✅ Python $python_version found"
else
    echo "❌ Error: Python 3 is required but not found"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Removing old one..."
    rm -rf venv
fi

python3 -m venv venv
if [ $? -eq 0 ]; then
    echo "✅ Virtual environment created"
else
    echo "❌ Error: Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✅ Python dependencies installed"
else
    echo "❌ Error: Failed to install Python dependencies"
    exit 1
fi

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
playwright install chromium
if [ $? -eq 0 ]; then
    echo "✅ Playwright browsers installed"
else
    echo "❌ Error: Failed to install Playwright browsers"
    exit 1
fi

# Check if Ollama is installed
echo "🤖 Checking Ollama installation..."
if command -v ollama &> /dev/null; then
    echo "✅ Ollama is already installed"
    ollama_version=$(ollama --version 2>&1)
    echo "   Version: $ollama_version"
else
    echo "⚠️  Ollama not found. Please install Ollama manually:"
    echo "   Linux: curl -fsSL https://ollama.ai/install.sh | sh"
    echo "   macOS: brew install ollama"
    echo "   Windows: Download from https://ollama.ai"
    echo ""
    echo "❓ Would you like to install Ollama automatically? (Linux only) [y/N]"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "📥 Installing Ollama..."
        curl -fsSL https://ollama.ai/install.sh | sh
        if [ $? -eq 0 ]; then
            echo "✅ Ollama installed successfully"
        else
            echo "❌ Error: Failed to install Ollama"
            exit 1
        fi
    else
        echo "⚠️  Please install Ollama manually and run this setup again"
        exit 1
    fi
fi

# Initialize database
echo "🗄️  Initializing database..."
python database.py
if [ $? -eq 0 ]; then
    echo "✅ Database initialized"
else
    echo "❌ Error: Database initialization failed"
    exit 1
fi

# Make start script executable
echo "🔧 Making start script executable..."
chmod +x start.sh
chmod +x setup.sh

echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo "✅ Virtual environment created and activated"
echo "✅ Python dependencies installed"
echo "✅ Playwright browsers installed"
echo "✅ Database initialized"
echo "✅ Scripts made executable"
echo ""
echo "🚀 Next Steps:"
echo "   1. Make sure Ollama is running: ollama serve"
echo "   2. Download the AI model: ollama pull gpt-oss:20b"
echo "   3. Start the application: ./start.sh"
echo ""
echo "📖 For detailed documentation, see PROJECT.md"
