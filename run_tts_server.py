#!/usr/bin/env python3
"""
Standalone launcher for the OpenAI-compatible TTS API server

Usage:
    python run_tts_server.py [--model MODEL_PATH] [--host HOST] [--port PORT]

Example:
    python run_tts_server.py --port 8000
    python run_tts_server.py --model path/to/model.gguf --port 5000
"""

import sys
import os

# Add src to path so we can import gguf_connector
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gguf_connector.tts_server import main

if __name__ == "__main__":
    main()
