"""
OpenAI-compatible TTS API Server for GGUF Models
This server provides a non-interactive API endpoint compatible with open-webui
for serving VibeVoice GGUF models for text-to-speech generation.
"""

import os
import io
import base64
from typing import Optional, List

# Check if core dependencies are available
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("Warning: torch not installed. Install with: pip install torch")

try:
    from fastapi import FastAPI, HTTPException, File, UploadFile
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import Response, JSONResponse
    from pydantic import BaseModel, Field
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("Warning: fastapi/uvicorn not installed. Install with: pip install fastapi uvicorn pydantic")

# Check if yvoice is available
try:
    from yvoice.modular.modeling_vibevoice_inference import VibeVoiceForConditionalGenerationInference
    from yvoice.processor.vibevoice_processor import VibeVoiceProcessor
    YVOICE_AVAILABLE = True
except ImportError:
    YVOICE_AVAILABLE = False
    print("Warning: yvoice not installed. Install with: pip install yvoice")

# Import gguf_connector utilities - these should always be available
try:
    from .tph import get_hf_cache_hub_path
    from .quant3 import convert_gguf_to_safetensors
    from .quant4 import add_metadata_to_safetensors
except ImportError:
    # Allow running standalone for testing
    try:
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
        from gguf_connector.tph import get_hf_cache_hub_path
        from gguf_connector.quant3 import convert_gguf_to_safetensors
        from gguf_connector.quant4 import add_metadata_to_safetensors
    except ImportError as e:
        print(f"Warning: Could not import gguf_connector utilities: {e}")


# Define data models only if FastAPI is available
if FASTAPI_AVAILABLE:
    class TTSRequest(BaseModel):
        """OpenAI-compatible TTS request model"""
        model: str = Field(default="vibevoice", description="The model to use for TTS")
        input: str = Field(..., description="The text to convert to speech")
        voice: str = Field(default="alloy", description="The voice to use")
        response_format: str = Field(default="mp3", description="Audio format (mp3, opus, aac, flac, wav, pcm)")
        speed: float = Field(default=1.0, description="Speech speed (0.25 to 4.0)")


    class ModelInfo(BaseModel):
        """Model information"""
        id: str
        object: str = "model"
        created: int = 1677649963
        owned_by: str = "gguf-connector"


    class ModelsResponse(BaseModel):
        """Models list response"""
        object: str = "list"
        data: List[ModelInfo]


if FASTAPI_AVAILABLE and TORCH_AVAILABLE:
    class TTSServer:
        """OpenAI-compatible TTS Server for GGUF models"""
        
        def __init__(self, model_path: Optional[str] = None, host: str = "0.0.0.0", port: int = 8000):
            self.app = FastAPI(
            title="GGUF TTS API",
            description="OpenAI-compatible TTS API for GGUF models",
            version="1.0.0"
        )
        self.host = host
        self.port = port
        self.model = None
        self.processor = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.dtype = torch.bfloat16 if torch.cuda.is_available() and torch.cuda.is_bf16_supported() else torch.float32
        self.model_path = model_path
        self.gguf_file = None
        
        # Setup CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Setup routes
        self.setup_routes()
        
    def setup_routes(self):
        """Setup API routes"""
        
        @self.app.get("/")
        async def root():
            return {
                "message": "GGUF TTS API Server",
                "endpoints": {
                    "/v1/audio/speech": "POST - Generate speech from text",
                    "/v1/models": "GET - List available models",
                    "/health": "GET - Health check"
                }
            }
        
        @self.app.get("/health")
        async def health():
            return {
                "status": "healthy",
                "model_loaded": self.model is not None,
                "device": self.device
            }
        
        @self.app.get("/v1/models")
        async def list_models():
            """List available models - OpenAI compatible endpoint"""
            models = []
            if self.gguf_file:
                models.append(ModelInfo(
                    id=f"vibevoice-{os.path.splitext(self.gguf_file)[0]}",
                    owned_by="gguf-connector"
                ))
            else:
                models.append(ModelInfo(
                    id="vibevoice",
                    owned_by="gguf-connector"
                ))
            return ModelsResponse(data=models)
        
        @self.app.post("/v1/audio/speech")
        async def create_speech(request: TTSRequest):
            """
            Generate speech from text - OpenAI compatible endpoint
            Compatible with open-webui TTS integration
            """
            if not YVOICE_AVAILABLE:
                raise HTTPException(
                    status_code=500,
                    detail="yvoice not installed. Install with: pip install yvoice"
                )
            
            if self.model is None:
                raise HTTPException(
                    status_code=503,
                    detail="Model not loaded. Please ensure a GGUF model is available."
                )
            
            try:
                # Generate speech
                audio_data = self._generate_speech(
                    text=request.input,
                    cfg_scale=request.speed
                )
                
                # Return audio in requested format
                # For now, we return WAV format regardless of requested format
                # The processor generates WAV files
                return Response(
                    content=audio_data,
                    media_type="audio/wav",
                    headers={
                        "Content-Disposition": "attachment; filename=speech.wav"
                    }
                )
                
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error generating speech: {str(e)}"
                )
    
    def _generate_speech(self, text: str, cfg_scale: float = 1.3) -> bytes:
        """
        Generate speech from text using the loaded model
        
        Args:
            text: Input text to convert to speech
            cfg_scale: Configuration scale for generation
            
        Returns:
            Audio data as bytes
        """
        if not text.strip():
            raise ValueError("Input text cannot be empty")
        
        # For simplicity, we'll use a default voice sample approach
        # In a production system, you'd want to have pre-configured voice samples
        # or allow uploading them via the API
        
        # Use text-only generation (without voice samples)
        # This is a simplified version - the full implementation would need voice samples
        inputs = self.processor(
            text=[text],
            return_tensors="pt",
            padding=True,
        )
        
        # Move inputs to device
        inputs = {
            key: val.to(self.device) if isinstance(val, torch.Tensor) else val 
            for key, val in inputs.items()
        }
        
        # Generate speech
        output = self.model.generate(
            **inputs,
            tokenizer=self.processor.tokenizer,
            cfg_scale=cfg_scale,
            max_new_tokens=None,
        )
        
        # Get generated speech
        generated_speech = output.speech_outputs[0]
        processor_sampling_rate = self.processor.audio_processor.sampling_rate
        
        # Save to bytes buffer
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        self.processor.save_audio(generated_speech, tmp_path, sampling_rate=processor_sampling_rate)
        
        # Read the file back
        with open(tmp_path, "rb") as f:
            audio_bytes = f.read()
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        return audio_bytes
    
    def load_model(self, gguf_path: str):
        """
        Load a GGUF model and prepare it for inference
        
        Args:
            gguf_path: Path to the GGUF model file
        """
        if not YVOICE_AVAILABLE:
            raise ImportError("yvoice not installed. Install with: pip install yvoice")
        
        print(f"Loading GGUF model: {gguf_path}")
        self.gguf_file = os.path.basename(gguf_path)
        
        # Get the model path for dequantization
        ghash = "53a915ae1a937cde20531290877f23aee39a7cc21786ff3a783158ac443ae74d"
        model_path = get_hf_cache_hub_path('callgg', 'vibevoice-bf16', ghash)
        
        # Dequantize the GGUF model
        use_bf16 = self.device == "cuda"
        print(f"Dequantizing GGUF model to: {model_path}")
        convert_gguf_to_safetensors(gguf_path, model_path, use_bf16)
        add_metadata_to_safetensors(model_path, {'format': 'pt'})
        
        # Load the model
        print(f"Loading VibeVoice model on {self.device} with dtype {self.dtype}")
        model_id = "callgg/vibevoice-bf16"
        
        self.model = VibeVoiceForConditionalGenerationInference.from_pretrained(
            model_id,
            dtype=self.dtype,
            device_map=self.device
        )
        
        self.processor = VibeVoiceProcessor.from_pretrained(model_id)
        
        print(f"Model loaded successfully!")
        print(f"Device: {self.device}")
        print(f"Dtype: {self.dtype}")
    
    def auto_load_model(self):
        """
        Automatically find and load a GGUF model from the current directory
        """
        current_dir = os.getcwd()
        gguf_files = [f for f in os.listdir(current_dir) if f.endswith('.gguf')]
        
        if not gguf_files:
            print("Warning: No GGUF files found in current directory")
            print("Place a VibeVoice GGUF model in the current directory and restart")
            return False
        
        if len(gguf_files) == 1:
            gguf_path = os.path.join(current_dir, gguf_files[0])
            print(f"Found GGUF model: {gguf_files[0]}")
            self.load_model(gguf_path)
            return True
        else:
            # Use the first one
            gguf_path = os.path.join(current_dir, gguf_files[0])
            print(f"Multiple GGUF files found. Using: {gguf_files[0]}")
            self.load_model(gguf_path)
            return True
    
    def run(self):
        """Start the server"""
        print(f"\n{'='*60}")
        print(f"Starting GGUF TTS API Server")
        print(f"{'='*60}")
        print(f"Host: {self.host}")
        print(f"Port: {self.port}")
        print(f"Device: {self.device}")
        print(f"Dtype: {self.dtype}")
        
        if self.model_path:
            self.load_model(self.model_path)
        else:
            self.auto_load_model()
        
        print(f"\nAPI Endpoints:")
        print(f"  - POST http://{self.host}:{self.port}/v1/audio/speech")
        print(f"  - GET  http://{self.host}:{self.port}/v1/models")
        print(f"  - GET  http://{self.host}:{self.port}/health")
        print(f"\nOpenAI-compatible TTS endpoint ready!")
        print(f"{'='*60}\n")
        
        uvicorn.run(self.app, host=self.host, port=self.port)


def main():
    """Main entry point for the TTS server"""
    import argparse
    
    # Check dependencies
    if not FASTAPI_AVAILABLE:
        print("Error: FastAPI not installed. Install with: pip install fastapi uvicorn pydantic")
        print("Or install all requirements: pip install -r requirements-tts-server.txt")
        return 1
    
    if not TORCH_AVAILABLE:
        print("Error: PyTorch not installed. Install with: pip install torch")
        print("Or install all requirements: pip install -r requirements-tts-server.txt")
        return 1
    
    parser = argparse.ArgumentParser(description="GGUF TTS API Server")
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Path to GGUF model file (auto-detects if not specified)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )
    
    args = parser.parse_args()
    
    server = TTSServer(model_path=args.model, host=args.host, port=args.port)
    server.run()
    return 0


if __name__ == "__main__":
    main()
