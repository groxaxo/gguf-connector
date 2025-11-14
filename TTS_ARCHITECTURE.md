# TTS API Server Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         External Clients                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │  open-webui  │  │  cURL/HTTP   │  │   Python     │              │
│  │              │  │   Clients    │  │    Apps      │              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
└─────────┼──────────────────┼──────────────────┼─────────────────────┘
          │                  │                  │
          │    HTTP/HTTPS    │                  │
          └──────────────────┴──────────────────┘
                             │
                ┌────────────▼────────────┐
                │   FastAPI Server        │
                │   (0.0.0.0:8000)       │
                │   + CORS Middleware     │
                └────────────┬────────────┘
                             │
        ┏━━━━━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━━━┓
        ┃          API Endpoints                    ┃
        ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
        ┃  POST /v1/audio/speech   (TTS)           ┃
        ┃  GET  /v1/models          (List Models)   ┃
        ┃  GET  /health             (Health Check)  ┃
        ┃  GET  /                   (API Info)      ┃
        ┗━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┛
                           │
        ┌──────────────────▼──────────────────┐
        │      TTSServer Class                │
        │  ┌───────────────────────────────┐  │
        │  │  - model: VibeVoice           │  │
        │  │  - processor: AudioProcessor  │  │
        │  │  - device: CUDA/CPU           │  │
        │  │  - dtype: bfloat16/float32    │  │
        │  └───────────────────────────────┘  │
        └──────────────────┬──────────────────┘
                           │
        ┌──────────────────▼──────────────────┐
        │     Model Loading Pipeline          │
        └──────────────────┬──────────────────┘
                           │
       ┌───────────────────┴────────────────────┐
       │                                        │
  ┌────▼─────┐                      ┌──────────▼────────┐
  │  GGUF    │                      │  Dequantization   │
  │  Files   │────────reads────────▶│  Process          │
  │  (.gguf) │                      │  (quant3/quant4)  │
  └──────────┘                      └──────────┬────────┘
                                               │
                                    ┌──────────▼────────┐
                                    │  Safetensors      │
                                    │  Files            │
                                    │  (.safetensors)   │
                                    └──────────┬────────┘
                                               │
                                    ┌──────────▼────────┐
                                    │  VibeVoice Model  │
                                    │  + Processor      │
                                    └──────────┬────────┘
                                               │
                ┌──────────────────────────────┴──────────────────┐
                │                                                 │
         ┌──────▼──────┐                               ┌─────────▼────────┐
         │  CUDA GPU   │                               │   CPU (Fallback) │
         │  bfloat16   │                               │   float32        │
         └─────────────┘                               └──────────────────┘
```

## Component Flow

### 1. Request Flow

```
┌─────────────┐
│   Client    │
│   Request   │
└──────┬──────┘
       │ POST /v1/audio/speech
       │ { "input": "text", "speed": 1.0 }
       │
┌──────▼────────────┐
│  FastAPI Server   │
│  - Validate Input │
│  - Parse JSON     │
└──────┬────────────┘
       │
┌──────▼────────────┐
│  TTSRequest Model │
│  - Pydantic       │
│  - Type Check     │
└──────┬────────────┘
       │
┌──────▼───────────────┐
│  _generate_speech()  │
│  - Process Text      │
│  - Tokenize          │
└──────┬───────────────┘
       │
┌──────▼───────────────┐
│  VibeVoice Model     │
│  - Generate Audio    │
│  - Tensor Output     │
└──────┬───────────────┘
       │
┌──────▼───────────────┐
│  Audio Processor     │
│  - Save to WAV       │
│  - Temp File         │
└──────┬───────────────┘
       │
┌──────▼───────────────┐
│  Response            │
│  - Read WAV File     │
│  - Return Binary     │
│  - Cleanup Temp      │
└──────┬───────────────┘
       │
┌──────▼──────┐
│   Client    │
│   WAV File  │
└─────────────┘
```

### 2. Model Loading Flow

```
┌──────────────────┐
│  Server Startup  │
└────────┬─────────┘
         │
    ┌────▼────────────────┐
    │  auto_load_model()  │
    │  - Scan directory   │
    │  - Find .gguf       │
    └────────┬────────────┘
             │
    ┌────────▼───────────────────┐
    │  convert_gguf_to_          │
    │  safetensors()             │
    │  - Dequantize GGUF         │
    │  - Save to HF cache        │
    └────────┬───────────────────┘
             │
    ┌────────▼───────────────────┐
    │  add_metadata_to_          │
    │  safetensors()             │
    │  - Add format metadata     │
    └────────┬───────────────────┘
             │
    ┌────────▼───────────────────┐
    │  VibeVoice.from_pretrained │
    │  - Load model              │
    │  - Setup device            │
    │  - Configure dtype         │
    └────────┬───────────────────┘
             │
    ┌────────▼───────────────────┐
    │  VibeVoiceProcessor.from_  │
    │  pretrained                │
    │  - Setup audio processor   │
    └────────┬───────────────────┘
             │
    ┌────────▼───────────────────┐
    │  Server Ready              │
    │  - Listen on port          │
    │  - Accept requests         │
    └────────────────────────────┘
```

## Component Details

### Core Components

#### 1. FastAPI Server
- **Location**: `src/gguf_connector/tts_server.py`
- **Role**: HTTP server, request routing, CORS handling
- **Dependencies**: `fastapi`, `uvicorn`, `pydantic`

#### 2. TTSServer Class
- **Location**: `src/gguf_connector/tts_server.py`
- **Role**: Main server logic, model management, request processing
- **Key Methods**:
  - `__init__()`: Initialize server
  - `setup_routes()`: Configure API endpoints
  - `load_model()`: Load GGUF model
  - `auto_load_model()`: Auto-detect and load
  - `_generate_speech()`: Generate audio from text
  - `run()`: Start server

#### 3. Model Loading Pipeline
- **GGUF Reader**: Reads quantized GGUF format
- **Dequantizer**: Converts to safetensors (bfloat16/float32)
- **Metadata Handler**: Adds required metadata
- **Model Loader**: Loads VibeVoice model
- **Processor Loader**: Loads audio processor

#### 4. Request/Response Models
- **TTSRequest**: Input validation
- **ModelInfo**: Model metadata
- **ModelsResponse**: Model list response

### Launcher Scripts

#### 1. Standalone Launcher
- **File**: `run_tts_server.py`
- **Purpose**: Start server from command line
- **Features**: Argument parsing, dependency checking

#### 2. Module Launcher
- **File**: `src/gguf_connector/api_tts.py`
- **Purpose**: Integration with gguf-connector package
- **Usage**: `ggc api_tts` (when installed)

### Testing & Documentation

#### 1. Test Suite
- **File**: `test_tts_api.py`
- **Tests**: Health, models, TTS generation
- **Features**: Configurable, skip options

#### 2. Example Scripts
- **File**: `examples_tts_api.sh`
- **Purpose**: Demonstrate API usage
- **Features**: Multiple examples, error handling

#### 3. Documentation
- **TTS_API.md**: API reference
- **QUICKSTART_TTS.md**: Quick start guide
- **TTS_SERVER_SUMMARY.md**: Implementation details
- **TTS_ARCHITECTURE.md**: This file

## Data Flow

### Text to Speech Generation

```
Text Input
    ↓
Tokenization (Processor)
    ↓
Model Input Tensor
    ↓
VibeVoice Model
    ↓
Speech Output Tensor
    ↓
Audio Processor
    ↓
WAV File
    ↓
Binary Response
    ↓
Client
```

### Model Format Conversion

```
GGUF File (quantized)
    ↓
Read metadata & tensors
    ↓
Dequantize (bfloat16/float32)
    ↓
Safetensors File
    ↓
Add metadata
    ↓
Load into memory
    ↓
VibeVoice Model
```

## Deployment Architecture

### Development

```
┌─────────────────┐
│  Developer PC   │
│  ├─ Python 3.8+ │
│  ├─ GGUF File   │
│  └─ Run Script  │
└────────┬────────┘
         │
         ▼
   localhost:8000
```

### Production (Single Server)

```
┌────────────────────┐
│  Production Server │
│  ├─ systemd        │
│  ├─ nginx (proxy)  │
│  ├─ TTS Server     │
│  └─ GPU/CPU        │
└────────┬───────────┘
         │
         ▼
   https://tts.example.com
```

### Production (Load Balanced)

```
                  ┌─────────────┐
                  │ Load Balancer│
                  └──────┬───────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼──────┐  ┌──────▼──────┐  ┌─────▼───────┐
│ TTS Server 1 │  │ TTS Server 2│  │ TTS Server 3│
│ + GPU        │  │ + GPU       │  │ + GPU       │
└──────────────┘  └─────────────┘  └─────────────┘
```

## Security Architecture

```
┌──────────────────────────────────────┐
│         Security Layers              │
├──────────────────────────────────────┤
│  1. CORS Policy                      │
│     - Configurable origins           │
│     - Method restrictions            │
├──────────────────────────────────────┤
│  2. Input Validation                 │
│     - Pydantic models                │
│     - Type checking                  │
│     - Length limits                  │
├──────────────────────────────────────┤
│  3. Error Handling                   │
│     - Graceful failures              │
│     - No sensitive data in errors    │
├──────────────────────────────────────┤
│  4. File Handling                    │
│     - Temporary files                │
│     - Automatic cleanup              │
│     - Secure paths                   │
├──────────────────────────────────────┤
│  5. Dependency Isolation             │
│     - Optional imports               │
│     - Version pinning                │
└──────────────────────────────────────┘
```

## Performance Considerations

### Latency Components

```
Request → Network → Server → Processing → Response
   |         |         |          |           |
  <1ms    5-50ms    <1ms    100ms-2s      5-50ms

Processing Breakdown:
- Text preprocessing: ~10ms
- Model inference: 50ms-2s (depends on length & device)
- Audio saving: ~50ms
- File reading: ~10ms
```

### Resource Usage

```
┌─────────────────────────────────────┐
│         Resource Profile            │
├─────────────────────────────────────┤
│  Memory (Model):  2-4 GB            │
│  Memory (Per Req): 100-500 MB       │
│  CPU (Idle):      <5%               │
│  CPU (Processing): 50-100%          │
│  GPU (Processing): 40-80%           │
│  Network:         Minimal           │
└─────────────────────────────────────┘
```

## Integration Points

### open-webui

```
┌──────────────┐
│  open-webui  │
│   Frontend   │
└──────┬───────┘
       │ TTS Request
       │
┌──────▼─────────────────────┐
│ OpenAI-Compatible Endpoint │
│ /v1/audio/speech           │
└──────┬─────────────────────┘
       │
┌──────▼─────────┐
│  TTS Server    │
│  GGUF Backend  │
└────────────────┘
```

### Custom Applications

```
┌──────────────┐
│   Your App   │
└──────┬───────┘
       │ HTTP POST
       │
┌──────▼─────────────────┐
│ Standard HTTP Client   │
│ (requests, fetch, etc) │
└──────┬─────────────────┘
       │
┌──────▼─────────┐
│  TTS Server    │
└────────────────┘
```

## Directory Structure

```
gguf-connector/
├── src/
│   └── gguf_connector/
│       ├── __init__.py
│       ├── tts_server.py      # Main server implementation
│       ├── api_tts.py          # Module launcher
│       ├── tph.py              # Path helpers
│       ├── quant3.py           # GGUF to safetensors
│       └── quant4.py           # Metadata handling
├── run_tts_server.py           # Standalone launcher
├── test_tts_api.py             # Test suite
├── examples_tts_api.sh         # Example scripts
├── requirements-tts-server.txt # Dependencies
├── TTS_API.md                  # API documentation
├── QUICKSTART_TTS.md           # Quick start guide
├── TTS_SERVER_SUMMARY.md       # Implementation summary
└── TTS_ARCHITECTURE.md         # This file
```

## Technology Stack

```
┌─────────────────────────────────────┐
│          Technology Stack           │
├─────────────────────────────────────┤
│  Web Framework:   FastAPI           │
│  ASGI Server:     Uvicorn           │
│  Validation:      Pydantic          │
│  ML Framework:    PyTorch           │
│  TTS Model:       VibeVoice         │
│  Model Format:    GGUF/Safetensors  │
│  Audio Format:    WAV               │
│  API Style:       REST/OpenAI       │
└─────────────────────────────────────┘
```

## Conclusion

This architecture provides:
- ✅ Clean separation of concerns
- ✅ Scalable design
- ✅ Easy deployment
- ✅ Secure implementation
- ✅ OpenAI compatibility
- ✅ Production readiness

The modular design allows for easy extension and customization while maintaining compatibility with existing OpenAI TTS clients.
