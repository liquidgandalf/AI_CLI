# System Specifications - Horizon Workstation

**Generated**: August 7, 2025  
**Purpose**: Home Assistant + Ollama AI Integration Project  
**System Name**: Horizon

## 🖥️ Hardware Specifications

### CPU
- **Processor**: AMD Ryzen 7 9700X 8-Core Processor
- **Architecture**: x86_64
- **Cores**: 8 physical cores
- **Threads**: 16 (2 threads per core)
- **Base Clock**: 600 MHz
- **Max Boost Clock**: 5,581 MHz (5.58 GHz)
- **Cache**: 
  - L1d: 384 KiB (8 instances)
  - L1i: 256 KiB (8 instances)
  - L2: 8 MiB (8 instances)
  - L3: 32 MiB (1 instance)
- **Features**: AVX512, AMD-V Virtualization, Hardware Security

### Memory (RAM)
- **Total RAM**: 64 GB (60 GiB usable)
- **Available**: 52 GiB free
- **Used**: 8.4 GiB
- **Swap**: 8 GB (unused)
- **Memory Type**: DDR5 (assumed based on Ryzen 9700X)

### GPU
- **Model**: NVIDIA GeForce RTX 4070 (16 GB VRAM)
- **Driver Version**: 535.230.02
- **CUDA Version**: 12.2
- **Memory**: 16,376 MiB total / 503 MiB used
- **Power**: 295W TDP (currently 5W idle)
- **Temperature**: 33°C (idle)
- **Utilization**: 1% (idle)

### Storage
- **Primary Drive**: NVMe SSD (nvme1n1)
- **Total Capacity**: 1.5 TB
- **Used**: 628 GB (46%)
- **Available**: 761 GB
- **File System**: ext4
- **Boot**: EFI (1.1 GB partition)

## 🐧 Operating System

- **OS**: Ubuntu 24.04.1 LTS
- **Kernel**: Linux 6.11.0-29-generic
- **Architecture**: x86_64
- **Desktop**: GNOME (based on running processes)
- **Hostname**: Horizon

## 🤖 AI/ML Environment

### Ollama Configuration
- **Version**: 0.11.3 (Updated)
- **Status**: ✅ Running
- **Service**: Systemd service active
- **API Endpoint**: http://localhost:11434
- **Memory Usage**: ~214 MB

### Available AI Models
| Model | ID | Size | Last Modified | Status |
|-------|----|----- |---------------|--------|
| **gpt-oss:20b** | - | 13.0 GB | Today | ⭐ Primary (NEW) |
| gemma3:12b | 6fd036cefda5 | 8.1 GB | 4 months ago | Available |
| mistral:latest | f974a74358d6 | 4.1 GB | 6 months ago | Available |
| deepseek-r1:14b | ea35dfe18182 | 9.0 GB | 6 months ago | Available |
| deepseek-r1:1.5b | a42b25d8c10a | 1.1 GB | 6 months ago | Available |
| llama3:8b | 365c0bd3c000 | 4.7 GB | 6 months ago | Available |
| llama3:latest | 365c0bd3c000 | 4.7 GB | 6 months ago | Available |

**Total Model Storage**: ~48 GB

## 🐍 Development Environment

### Python
- **Version**: Python 3.12.3
- **Package Manager**: pip
- **Virtual Environments**: venv support

### Current Running Services
- **Ollama**: AI model serving (port 11434)
- **AI Chat Interface**: Flask app (port 5785)
- **X11/Wayland**: Display server
- **GNOME Shell**: Desktop environment
- **Firefox**: Web browser

## 🌐 Network & Connectivity

### Current Ports in Use
- **5785**: AI Chat Interface (Flask)
- **11434**: Ollama API service
- **Display**: :0 (X11)

### Network Interfaces
- **Localhost**: 127.0.0.1 (loopback)
- **LAN**: Available for Home Assistant integration

## 🔧 Performance Characteristics

### AI Model Performance Estimates
Based on hardware specifications:

| Model | VRAM Usage | CPU Usage | Inference Speed | Recommended Use |
|-------|------------|-----------|-----------------|-----------------|
| **gemma3:12b** | ~8-10 GB | Medium | Fast | ⭐ Production |
| deepseek-r1:14b | ~10-12 GB | High | Medium | Complex tasks |
| llama3:8b | ~6-8 GB | Low | Very Fast | Quick responses |
| mistral:latest | ~4-6 GB | Low | Very Fast | Lightweight tasks |

### System Capacity
- **Concurrent Models**: Can run 1-2 large models simultaneously
- **GPU Acceleration**: Full CUDA support available
- **Memory Headroom**: 52 GB available for additional services
- **Storage**: 761 GB free for model downloads and data

## 🏠 Home Assistant Integration Readiness

### Networking
- ✅ **Local API Access**: Ollama accessible on localhost:11434
- ✅ **HTTP/REST**: Standard REST API available
- ✅ **JSON Communication**: Full JSON request/response support
- ✅ **No Authentication Required**: Local access (can add if needed)

### Recommended Integration Methods
1. **REST API Calls**: Direct HTTP requests to Ollama
2. **Custom Component**: Python-based HA integration
3. **MQTT Bridge**: Via custom service (if needed)
4. **Webhooks**: For event-driven responses

### Performance Considerations
- **Response Time**: 1-5 seconds for typical queries
- **Concurrent Requests**: 2-4 simultaneous (depending on model)
- **Memory Impact**: ~8-12 GB per active model
- **CPU Impact**: Moderate (8-core CPU can handle background processing)

## 🔐 Security & Access

### Current Security Status
- **Firewall**: Standard Ubuntu firewall
- **Local Only**: Services bound to localhost
- **User Permissions**: Standard user account
- **GPU Access**: NVIDIA drivers with user access

### Recommendations for HA Integration
- **Network Isolation**: Keep on local network
- **API Keys**: Consider adding authentication for external access
- **Rate Limiting**: Implement if exposing beyond local network
- **Monitoring**: Track resource usage and response times

## 📊 Resource Monitoring

### Current Usage (Idle)
- **CPU**: ~5% (background tasks)
- **RAM**: 8.4 GB / 64 GB (13%)
- **GPU**: 1% utilization
- **Storage**: 46% used
- **Network**: Minimal

### Recommended Monitoring for HA
- **Ollama Process**: Memory and CPU usage
- **Model Loading**: VRAM consumption
- **API Response Times**: Latency tracking
- **Queue Depth**: Concurrent request handling

## 🎯 Optimization Recommendations

### For Home Assistant Integration
1. **Model Selection**: Use llama3:8b for fast responses, gemma3:12b for quality
2. **Request Queuing**: Implement queue management in HA
3. **Caching**: Cache common responses
4. **Fallback**: Have lightweight model as backup
5. **Resource Limits**: Set memory/CPU limits if needed

### System Tuning
- **GPU Memory**: 16 GB VRAM allows for large models
- **System RAM**: 64 GB provides excellent headroom
- **Storage**: Consider SSD optimization for model loading
- **Network**: Local network should provide <1ms latency

---

**System Status**: ✅ **Optimal for AI/ML workloads**  
**HA Integration**: ✅ **Ready for implementation**  
**Performance**: ✅ **High-end configuration**  
**Reliability**: ✅ **Stable platform**
