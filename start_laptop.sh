#!/bin/bash
# Laptop deployment script for AI_CLI
# This configures the app to use the GPU server at 192.168.0.5

echo "Starting AI_CLI in laptop mode..."
echo "Using GPU server at 192.168.0.5 for AI processing"

# Set environment variable to use GPU server
export OLLAMA_URL="http://192.168.0.5:11434/api/generate"

# Start the Flask app
python3 app.py
