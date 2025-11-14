# GGUF TTS API Server

OpenAI-compatible Text-to-Speech API server for GGUF models, specifically designed for VibeVoice models and compatible with open-webui.

## Features

- ✅ OpenAI-compatible API endpoints
- ✅ Non-interactive server operation
- ✅ Automatic GGUF model detection and loading
- ✅ Compatible with open-webui TTS integration
- ✅ CUDA acceleration support
- ✅ CORS enabled for web integration

## Requirements

Install the required dependencies:

```bash
pip install fastapi uvicorn pydantic torch yvoice
```

Additional dependencies from gguf-connector:
- `torch` - PyTorch for model inference
- `yvoice` - VibeVoice TTS model implementation
- `safetensors` - For model format conversion

## Quick Start

1. **Download a VibeVoice GGUF model** from HuggingFace:
   - Example: https://huggingface.co/gguf-org/vibevoice-gguf

2. **Place the GGUF file in your working directory**

3. **Start the server**:
   ```bash
   python run_tts_server.py
   ```

   Or with custom options:
   ```bash
   python run_tts_server.py --host 0.0.0.0 --port 8000 --model path/to/model.gguf
   ```

4. **The server will start** on `http://0.0.0.0:8000`

## API Endpoints

### 1. Generate Speech (OpenAI-compatible)

**Endpoint**: `POST /v1/audio/speech`

**Request Body**:
```json
{
  "model": "vibevoice",
  "input": "Hello, this is a test of the text to speech system.",
  "voice": "alloy",
  "response_format": "wav",
  "speed": 1.0
}
```

**Parameters**:
- `model` (string): Model identifier (default: "vibevoice")
- `input` (string, required): Text to convert to speech
- `voice` (string): Voice identifier (default: "alloy")
- `response_format` (string): Audio format - mp3, opus, aac, flac, wav, pcm (currently returns wav)
- `speed` (float): Speech speed from 0.25 to 4.0 (default: 1.0)

**Response**: Audio file (WAV format)

**cURL Example**:
```bash
curl -X POST http://localhost:8000/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "model": "vibevoice",
    "input": "Hello world!",
    "voice": "alloy",
    "speed": 1.0
  }' \
  --output speech.wav
```

**Python Example**:
```python
import requests

response = requests.post(
    "http://localhost:8000/v1/audio/speech",
    json={
        "model": "vibevoice",
        "input": "Hello, this is a test!",
        "voice": "alloy",
        "speed": 1.0
    }
)

with open("output.wav", "wb") as f:
    f.write(response.content)
```

### 2. List Models

**Endpoint**: `GET /v1/models`

**Response**:
```json
{
  "object": "list",
  "data": [
    {
      "id": "vibevoice-model_name",
      "object": "model",
      "created": 1677649963,
      "owned_by": "gguf-connector"
    }
  ]
}
```

### 3. Health Check

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "device": "cuda"
}
```

### 4. Root

**Endpoint**: `GET /`

**Response**: API information and available endpoints

## Integration with open-webui

To use this TTS server with open-webui:

1. **Start the TTS server** on your desired port (e.g., 8000)

2. **Configure open-webui** to use the TTS endpoint:
   - Set the TTS API URL to: `http://localhost:8000/v1/audio/speech`
   - The endpoint is OpenAI-compatible, so it should work seamlessly

3. **Test the integration** by generating speech in open-webui

## Command-Line Options

```
python run_tts_server.py --help

Options:
  --model MODEL    Path to GGUF model file (auto-detects if not specified)
  --host HOST      Host to bind to (default: 0.0.0.0)
  --port PORT      Port to bind to (default: 8000)
```

## Model Auto-Detection

If you don't specify a model path, the server will:
1. Search for `.gguf` files in the current directory
2. Automatically load the first GGUF file found
3. If multiple files exist, it uses the first one

## Technical Details

### Model Loading Process

1. **GGUF Detection**: Server searches for `.gguf` files
2. **Dequantization**: Converts GGUF to safetensors format
3. **Model Loading**: Loads the VibeVoice model using yvoice
4. **Device Selection**: Automatically uses CUDA if available, otherwise CPU
5. **Precision**: Uses bfloat16 on CUDA, float32 on CPU

### Architecture

- **FastAPI**: Modern web framework for the API
- **Uvicorn**: ASGI server for production deployment
- **VibeVoice**: State-of-the-art TTS model
- **GGUF**: Efficient model format for inference

## Troubleshooting

### "yvoice not installed"
```bash
pip install yvoice
```

### "No GGUF files found"
- Download a VibeVoice GGUF model from HuggingFace
- Place it in the same directory as the server script

### CUDA out of memory
- The server uses bfloat16 on CUDA for efficiency
- If you encounter OOM errors, try using CPU mode or a smaller model

### Port already in use
```bash
python run_tts_server.py --port 5000
```

## Production Deployment

For production use, consider:

1. **Process Management**: Use systemd, supervisor, or PM2
2. **Reverse Proxy**: Use nginx or Apache for SSL/TLS
3. **Resource Limits**: Set appropriate memory and CPU limits
4. **Monitoring**: Implement logging and health checks
5. **Security**: Add authentication/authorization if needed

### Example systemd service

Create `/etc/systemd/system/gguf-tts.service`:

```ini
[Unit]
Description=GGUF TTS API Server
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/gguf-connector
ExecStart=/usr/bin/python3 run_tts_server.py --host 0.0.0.0 --port 8000
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable gguf-tts
sudo systemctl start gguf-tts
sudo systemctl status gguf-tts
```

## Contributing

To contribute improvements or report issues, please visit the repository.

## License

This project follows the same license as the gguf-connector package.
