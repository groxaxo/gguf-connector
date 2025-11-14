"""
Launcher for the OpenAI-compatible TTS API server
Command: ggc api_tts or ggc tts_api
"""

from .tts_server import main

if __name__ == "__main__":
    main()
