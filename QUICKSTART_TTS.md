# Quick Start Guide: GGUF TTS API Server

This guide will help you quickly set up and run the OpenAI-compatible TTS API server for GGUF models.

## Prerequisites

- Python 3.8 or higher
- pip package manager
- (Optional) CUDA-capable GPU for faster inference

## Installation

### Step 1: Install Dependencies

```bash
pip install -r requirements-tts-server.txt
```

Or install individual packages:

```bash
pip install fastapi uvicorn pydantic torch yvoice safetensors numpy
```

### Step 2: Download a GGUF Model

Download a VibeVoice GGUF model from HuggingFace:

```bash
# Using git lfs (if available)
git lfs install
git clone https://huggingface.co/gguf-org/vibevoice-gguf

# Or download manually from:
# https://huggingface.co/gguf-org/vibevoice-gguf
```

Place the `.gguf` file in your working directory.

## Running the Server

### Option 1: Auto-detect Model (Recommended)

If you have a single GGUF file in the current directory:

```bash
python run_tts_server.py
```

### Option 2: Specify Model Path

```bash
python run_tts_server.py --model path/to/your/model.gguf
```

### Option 3: Custom Host and Port

```bash
python run_tts_server.py --host 0.0.0.0 --port 5000
```

## Testing the Server

### 1. Check Server Health

```bash
curl http://localhost:8000/health
```

### 2. List Available Models

```bash
curl http://localhost:8000/v1/models
```

### 3. Generate Speech

```bash
curl -X POST http://localhost:8000/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "model": "vibevoice",
    "input": "Hello! Welcome to the GGUF TTS API server.",
    "voice": "alloy",
    "speed": 1.0
  }' \
  --output speech.wav
```

### 4. Play the Generated Audio

```bash
# On Linux
aplay speech.wav

# On macOS
afplay speech.wav

# On Windows
start speech.wav
```

## Using the Test Script

Run the automated test suite:

```bash
# Test all endpoints (requires model to be loaded)
python test_tts_api.py

# Test without TTS generation
python test_tts_api.py --skip-tts

# Test on a different port
python test_tts_api.py --url http://localhost:5000
```

## Integration with open-webui

1. **Start the TTS server:**
   ```bash
   python run_tts_server.py --host 0.0.0.0 --port 8000
   ```

2. **Configure open-webui:**
   - Go to Settings → Audio
   - Set TTS Engine to "OpenAI"
   - Set TTS API URL to: `http://localhost:8000/v1/audio/speech`
   - Save settings

3. **Test in open-webui:**
   - Type a message in the chat
   - Click the "Read Aloud" button
   - The server will generate speech using your GGUF model

## Troubleshooting

### Server won't start

**Problem:** "Error: FastAPI not installed"

**Solution:**
```bash
pip install fastapi uvicorn pydantic
```

---

**Problem:** "Error: PyTorch not installed"

**Solution:**
```bash
pip install torch
```

---

**Problem:** "Warning: yvoice not installed"

**Solution:**
```bash
pip install yvoice
```

### No GGUF files found

**Problem:** "Warning: No GGUF files found in current directory"

**Solution:**
1. Download a VibeVoice GGUF model
2. Place it in the same directory as `run_tts_server.py`
3. Or specify the path: `python run_tts_server.py --model /path/to/model.gguf`

### CUDA out of memory

**Problem:** GPU runs out of memory during inference

**Solution:**
- Use CPU mode (server will auto-fallback if GPU is unavailable)
- Use a smaller quantized model
- Close other GPU-intensive applications

### Connection refused

**Problem:** Can't connect to the server

**Solution:**
1. Check if the server is running: `curl http://localhost:8000/health`
2. Verify the port is correct
3. Check firewall settings
4. Ensure no other service is using the port

## Advanced Usage

### Running as a Background Service

#### Using nohup (Linux/macOS)

```bash
nohup python run_tts_server.py > tts_server.log 2>&1 &
```

#### Using screen (Linux/macOS)

```bash
screen -S tts-server
python run_tts_server.py
# Press Ctrl+A, then D to detach
```

#### Using systemd (Linux)

Create `/etc/systemd/system/gguf-tts.service`:

```ini
[Unit]
Description=GGUF TTS API Server
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/gguf-connector
ExecStart=/usr/bin/python3 run_tts_server.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable gguf-tts
sudo systemctl start gguf-tts
sudo systemctl status gguf-tts
```

### Environment Variables

You can also use environment variables:

```bash
export TTS_HOST=0.0.0.0
export TTS_PORT=8000
export TTS_MODEL=/path/to/model.gguf
python run_tts_server.py
```

## Python API Example

```python
import requests
import json

def generate_speech(text, output_file="output.wav", server_url="http://localhost:8000"):
    """Generate speech from text using the TTS API"""
    
    response = requests.post(
        f"{server_url}/v1/audio/speech",
        json={
            "model": "vibevoice",
            "input": text,
            "voice": "alloy",
            "speed": 1.0
        },
        timeout=120
    )
    
    if response.status_code == 200:
        with open(output_file, "wb") as f:
            f.write(response.content)
        print(f"Speech saved to {output_file}")
        return True
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return False

# Usage
generate_speech("Hello, this is a test of the TTS system!")
```

## Next Steps

- Read the full [API Documentation](TTS_API.md)
- Explore voice customization options
- Integrate with your applications
- Set up monitoring and logging for production use

## Support

For issues, questions, or contributions, please visit the repository or consult the main [README](README.md).
