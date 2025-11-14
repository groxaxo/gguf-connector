# Backend Integration Guide

This guide explains how to integrate the futuristic frontend with GGUF Connector backends.

## Overview

The frontend is designed as a pure HTML/CSS/JavaScript application that communicates with backend services via REST APIs. It's currently in demo mode but ready for backend integration.

## Architecture

```
┌─────────────────┐
│  Web Browser    │
│  (Frontend UI)  │
└────────┬────────┘
         │ HTTP/WebSocket
         ▼
┌─────────────────┐
│  Backend API    │
│  (FastAPI/Flask)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  GGUF Models    │
│  & Tools        │
└─────────────────┘
```

## API Endpoints to Implement

### 1. Chat API

**Endpoint**: `POST /api/chat`

**Request**:
```json
{
  "model": "llama-2-7b-chat.gguf",
  "message": "Hello, how are you?",
  "history": [
    {"role": "user", "content": "Previous message"},
    {"role": "assistant", "content": "Previous response"}
  ]
}
```

**Response**:
```json
{
  "response": "I'm doing well, thank you for asking!",
  "model": "llama-2-7b-chat.gguf"
}
```

**Implementation Example**:
```python
from fastapi import FastAPI, HTTPException
from ctransformers import AutoModelForCausalLM

app = FastAPI()
models = {}

@app.post("/api/chat")
async def chat(request: dict):
    model_name = request["model"]
    message = request["message"]
    
    # Load model if not cached
    if model_name not in models:
        models[model_name] = AutoModelForCausalLM.from_pretrained(model_name)
    
    # Generate response
    response = models[model_name](message)
    
    return {"response": response, "model": model_name}
```

### 2. Image Generation API

**Endpoint**: `POST /api/generate-image`

**Request**:
```json
{
  "model": "flux",
  "prompt": "A futuristic cityscape at night",
  "width": 1024,
  "height": 1024,
  "steps": 25,
  "guidance": 7.5
}
```

**Response**:
```json
{
  "image": "data:image/png;base64,iVBORw0KG...",
  "seed": 12345
}
```

**Implementation Example**:
```python
import base64
from io import BytesIO
from diffusers import FluxPipeline

@app.post("/api/generate-image")
async def generate_image(request: dict):
    # Load appropriate pipeline based on model
    pipe = FluxPipeline.from_pretrained("black-forest-labs/FLUX.1-dev")
    
    # Generate image
    image = pipe(
        prompt=request["prompt"],
        width=request["width"],
        height=request["height"],
        num_inference_steps=request["steps"],
        guidance_scale=request["guidance"]
    ).images[0]
    
    # Convert to base64
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return {"image": f"data:image/png;base64,{img_str}"}
```

### 3. Image Editing API

**Endpoint**: `POST /api/edit-image`

**Request**:
```json
{
  "image": "data:image/png;base64,iVBORw0KG...",
  "instruction": "Add a hat to the person",
  "guidance": 2.5
}
```

**Response**:
```json
{
  "image": "data:image/png;base64,iVBORw0KG..."
}
```

### 4. Text-to-Speech API

**Endpoint**: `POST /api/tts`

**Request**:
```json
{
  "model": "vibevoice",
  "text": "Hello, this is a test.",
  "voice": "alloy",
  "speed": 1.0
}
```

**Response**:
```json
{
  "audio": "data:audio/wav;base64,UklGRiQAAA..."
}
```

**Note**: The TTS server (`run_tts_server.py`) already implements an OpenAI-compatible API at `/v1/audio/speech`.

### 5. Model Management API

**Endpoint**: `GET /api/models`

**Response**:
```json
{
  "models": [
    {
      "name": "llama-2-7b-chat.gguf",
      "size": "3.8 GB",
      "type": "chat",
      "quantization": "Q4_K_M"
    }
  ]
}
```

**Implementation**:
```python
import os
from pathlib import Path

@app.get("/api/models")
async def list_models():
    models = []
    for file in Path(".").glob("*.gguf"):
        size = file.stat().st_size / (1024**3)  # Convert to GB
        models.append({
            "name": file.name,
            "size": f"{size:.1f} GB",
            "type": "gguf"
        })
    return {"models": models}
```

### 6. GGUF Tools APIs

**Convert**: `POST /api/tools/convert`
```json
{
  "input_file": "model.safetensors",
  "output_format": "gguf"
}
```

**Quantize**: `POST /api/tools/quantize`
```json
{
  "input_file": "model.safetensors",
  "quantization": "q4_0"
}
```

**Merge**: `POST /api/tools/merge`
```json
{
  "input_files": ["model1.gguf", "model2.gguf"],
  "output_file": "merged.gguf"
}
```

## Frontend Code Modifications

### Update API Base URL

In `frontend/script.js`, add a configuration object at the top:

```javascript
const API_CONFIG = {
    baseUrl: 'http://localhost:8000',  // Your backend URL
    endpoints: {
        chat: '/api/chat',
        generateImage: '/api/generate-image',
        editImage: '/api/edit-image',
        tts: '/api/tts',
        models: '/api/models'
    }
};
```

### Example: Chat Implementation

Replace the demo chat function with:

```javascript
async function sendChatMessage(model, message, history) {
    showLoading();
    
    try {
        const response = await fetch(`${API_CONFIG.baseUrl}${API_CONFIG.endpoints.chat}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                model: model,
                message: message,
                history: history
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        hideLoading();
        return data.response;
        
    } catch (error) {
        hideLoading();
        showNotification('Error: ' + error.message, 'error');
        return null;
    }
}
```

## CORS Configuration

If your frontend and backend are on different ports, you need to enable CORS:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## WebSocket Support (Optional)

For real-time streaming responses, implement WebSocket endpoints:

```python
from fastapi import WebSocket

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    
    while True:
        data = await websocket.receive_json()
        model_name = data["model"]
        message = data["message"]
        
        # Stream response token by token
        for token in model.generate_stream(message):
            await websocket.send_json({"token": token})
```

Frontend:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    appendToMessage(data.token);
};
```

## Testing Integration

1. **Start Backend**:
```bash
uvicorn backend:app --reload --port 8000
```

2. **Start Frontend**:
```bash
python run_frontend.py
```

3. **Test API**:
```bash
curl -X POST http://localhost:8000/api/models
```

## Security Considerations

1. **Authentication**: Add API key or OAuth2 authentication
2. **Rate Limiting**: Prevent abuse with rate limits
3. **Input Validation**: Validate all user inputs
4. **File Upload Limits**: Set maximum file sizes
5. **HTTPS**: Use HTTPS in production

## Production Deployment

### Backend
- Use production ASGI server (Gunicorn + Uvicorn)
- Set up reverse proxy (Nginx)
- Enable HTTPS with SSL certificates
- Configure logging and monitoring

### Frontend
- Serve static files from CDN
- Enable caching headers
- Minify CSS/JS (optional)
- Add analytics (optional)

## Example: Complete Backend Server

See `example_backend.py` for a complete implementation (to be created).

## Support

For questions or issues with integration:
1. Check existing backend implementations in `src/gguf_connector/`
2. Review FastAPI documentation
3. Open an issue on GitHub

Happy integrating! 🚀
