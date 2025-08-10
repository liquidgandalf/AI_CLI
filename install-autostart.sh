#!/bin/bash

# AI Chat Interface Auto-Start Installation Script
# This script sets up the AI Chat system to start automatically on boot

echo "🚀 Installing AI Chat Auto-Start Service..."
echo "==========================================="

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please do not run this script as root. Run as your regular user."
    echo "   The script will ask for sudo password when needed."
    exit 1
fi

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if required files exist
if [ ! -f "ai-chat.service" ]; then
    echo "❌ Error: ai-chat.service file not found"
    exit 1
fi

if [ ! -f "start-daemon.sh" ]; then
    echo "❌ Error: start-daemon.sh file not found"
    exit 1
fi

# Make sure daemon script is executable
chmod +x start-daemon.sh

echo "📋 Current user: $(whoami)"
echo "📁 Installation directory: $SCRIPT_DIR"

# Update the service file with correct paths and user
echo "🔧 Updating service file with current paths..."
sed -i "s|User=derek|User=$(whoami)|g" ai-chat.service
sed -i "s|Group=derek|Group=$(whoami)|g" ai-chat.service
sed -i "s|WorkingDirectory=/home/derek/AI_CLI|WorkingDirectory=$SCRIPT_DIR|g" ai-chat.service
sed -i "s|ExecStart=/home/derek/AI_CLI/start.sh|ExecStart=$SCRIPT_DIR/start-daemon.sh|g" ai-chat.service
sed -i "s|Environment=PYTHONPATH=/home/derek/AI_CLI|Environment=PYTHONPATH=$SCRIPT_DIR|g" ai-chat.service
sed -i "s|Environment=PATH=/home/derek/AI_CLI/venv/bin|Environment=PATH=$SCRIPT_DIR/venv/bin|g" ai-chat.service

# Copy service file to systemd directory
echo "📦 Installing systemd service..."
sudo cp ai-chat.service /etc/systemd/system/

# Reload systemd and enable the service
echo "🔄 Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "✅ Enabling AI Chat service..."
sudo systemctl enable ai-chat.service

echo ""
echo "🎉 Installation Complete!"
echo "========================"
echo ""
echo "Your AI Chat Interface is now configured to start automatically on boot."
echo ""
echo "Available commands:"
echo "  sudo systemctl start ai-chat     # Start the service now"
echo "  sudo systemctl stop ai-chat      # Stop the service"
echo "  sudo systemctl restart ai-chat   # Restart the service"
echo "  sudo systemctl status ai-chat    # Check service status"
echo "  sudo journalctl -u ai-chat -f    # View live logs"
echo ""
echo "The service will:"
echo "  ✅ Start automatically on boot"
echo "  ✅ Restart automatically if it crashes"
echo "  ✅ Run the Flask app on http://localhost:5785"
echo "  ✅ Run the background file processor"
echo "  ✅ Log output to logs/ directory and systemd journal"
echo ""
echo "To start the service now, run:"
echo "  sudo systemctl start ai-chat"
echo ""
echo "To test auto-start, reboot your system:"
echo "  sudo reboot"
echo ""
