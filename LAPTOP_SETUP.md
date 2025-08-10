# AI_CLI Laptop Setup Instructions

This guide will help you set up AI_CLI on your laptop to use your GPU server (192.168.0.5) for AI processing.

## 📋 Prerequisites

- **Python 3.8+** installed on your laptop
- **Network access** to your GPU server (192.168.0.5)
- **Same WiFi/LAN** as your GPU server

## 🚀 Quick Setup Steps

### 1. Copy Files to Your Laptop

**Option A: Using SCP (if SSH is enabled on server)**
```bash
scp -r derek@192.168.0.5:/home/derek/AI_CLI /path/to/your/laptop/
```

**Option B: Using USB/External Drive**
- Copy the entire `AI_CLI` folder to your laptop
- Place it anywhere you like (e.g., `~/AI_CLI` or `~/Documents/AI_CLI`)

### 2. Install Python Dependencies

```bash
cd AI_CLI
pip install -r requirements.txt
```

**If you don't have pip:**
```bash
# On Ubuntu/Debian:
sudo apt update && sudo apt install python3-pip

# On macOS:
brew install python3

# On Windows:
# Download Python from python.org (includes pip)
```

### 3. Start the Application

**Easy Method (Recommended):**
```bash
./start_laptop.sh
```

**Manual Method:**
```bash
export OLLAMA_URL="http://192.168.0.5:11434/api/generate"
python3 app.py
```

### 4. Access the Application

Open your web browser and go to:
```
http://localhost:5785
```

## 🔧 Troubleshooting

### Problem: "Connection refused" or "Cannot connect to Ollama"

**Solution 1: Test server connection**
```bash
curl http://192.168.0.5:11434/api/tags
```
If this fails, the server might not be accessible.

**Solution 2: Check if both devices are on same network**
```bash
ping 192.168.0.5
```

**Solution 3: Verify server is running**
Ask someone to check on the server:
```bash
systemctl status ollama
netstat -tlnp | grep 11434
```

### Problem: "Module not found" errors

**Solution: Install missing dependencies**
```bash
pip install flask requests beautifulsoup4 flask-login sqlalchemy werkzeug markdown playwright
```

### Problem: Permission denied on start_laptop.sh

**Solution: Make script executable**
```bash
chmod +x start_laptop.sh
```

### Problem: Database errors

**Solution: The SQLite database should work as-is, but if you get errors:**
```bash
# Remove database to start fresh (you'll lose data)
rm ai_chat.db
python3 app.py  # Will recreate database
```

## 📊 What Works on Laptop

✅ **Full web interface** - All UI features work normally
✅ **User accounts** - Login with your existing account
✅ **File uploads** - Upload and manage files
✅ **Conversations** - All your chat history
✅ **Projects** - Project management features
✅ **GPU processing** - AI requests processed on server GPU

## 🔒 Security Notes

- The app runs on `localhost:5785` (only accessible from your laptop)
- AI processing happens on your server (192.168.0.5)
- Database and files are local to your laptop
- No external internet access required for AI (uses local server)

## ⚡ Performance Expectations

- **Web Interface**: Fast and responsive
- **AI Responses**: Same speed as server (GPU-accelerated)
- **File Operations**: Local laptop speed
- **Network Latency**: Minimal on local network

## 🛠 Advanced Configuration

### Change Server IP
If your server IP changes, edit the startup script:
```bash
nano start_laptop.sh
# Change: export OLLAMA_URL="http://NEW_IP:11434/api/generate"
```

### Run on Different Port
```bash
export OLLAMA_URL="http://192.168.0.5:11434/api/generate"
python3 app.py --port 8080  # Note: This may require code modification
```

### Environment Variables
You can set these permanently in your shell profile:
```bash
echo 'export OLLAMA_URL="http://192.168.0.5:11434/api/generate"' >> ~/.bashrc
source ~/.bashrc
```

## 📞 Getting Help

If you encounter issues:

1. **Check server status** - Make sure the GPU server is running
2. **Test network connection** - Use `ping 192.168.0.5`
3. **Check logs** - Look for error messages in the terminal
4. **Restart both** - Restart the laptop app and server if needed

## 🎯 Success Indicators

You'll know it's working when:
- ✅ Browser opens to `http://localhost:5785`
- ✅ You can log in with your existing account
- ✅ AI responses appear (processed on GPU server)
- ✅ No "connection refused" errors in terminal

---

**That's it!** Your laptop is now running the AI_CLI interface while your server handles the heavy GPU processing. Enjoy the best of both worlds! 🚀
