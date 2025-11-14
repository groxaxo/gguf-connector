#!/bin/bash
# Example API calls for the GGUF TTS API Server
# Make sure the server is running before executing these commands

# Set the base URL
BASE_URL="http://localhost:8000"

echo "======================================"
echo "GGUF TTS API - Example Commands"
echo "======================================"
echo ""

# 1. Check server health
echo "1. Checking server health..."
curl -s "${BASE_URL}/health" | jq '.' || curl -s "${BASE_URL}/health"
echo ""
echo ""

# 2. List available models
echo "2. Listing available models..."
curl -s "${BASE_URL}/v1/models" | jq '.' || curl -s "${BASE_URL}/v1/models"
echo ""
echo ""

# 3. Generate simple speech
echo "3. Generating simple speech..."
curl -X POST "${BASE_URL}/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "vibevoice",
    "input": "Hello! This is a test of the text to speech system.",
    "voice": "alloy",
    "speed": 1.0
  }' \
  --output example_1.wav

if [ -f "example_1.wav" ]; then
    echo "✅ Speech saved to example_1.wav"
else
    echo "❌ Failed to generate speech"
fi
echo ""
echo ""

# 4. Generate speech with custom speed
echo "4. Generating speech with slower speed..."
curl -X POST "${BASE_URL}/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "vibevoice",
    "input": "This speech is generated at a slower pace for better clarity.",
    "voice": "alloy",
    "speed": 0.8
  }' \
  --output example_2_slow.wav

if [ -f "example_2_slow.wav" ]; then
    echo "✅ Slow speech saved to example_2_slow.wav"
else
    echo "❌ Failed to generate speech"
fi
echo ""
echo ""

# 5. Generate speech with faster speed
echo "5. Generating speech with faster speed..."
curl -X POST "${BASE_URL}/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "vibevoice",
    "input": "This speech is generated at a faster pace.",
    "voice": "alloy",
    "speed": 1.5
  }' \
  --output example_3_fast.wav

if [ -f "example_3_fast.wav" ]; then
    echo "✅ Fast speech saved to example_3_fast.wav"
else
    echo "❌ Failed to generate speech"
fi
echo ""
echo ""

# 6. Generate longer speech
echo "6. Generating longer speech..."
curl -X POST "${BASE_URL}/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "vibevoice",
    "input": "Welcome to the GGUF TTS API server. This is a comprehensive text-to-speech system that uses GGUF models for efficient inference. You can use this API to generate high-quality speech from text in your applications. The API is compatible with OpenAI standards, making it easy to integrate with existing tools like open-webui.",
    "voice": "alloy",
    "speed": 1.0
  }' \
  --output example_4_long.wav

if [ -f "example_4_long.wav" ]; then
    echo "✅ Long speech saved to example_4_long.wav"
else
    echo "❌ Failed to generate speech"
fi
echo ""
echo ""

echo "======================================"
echo "All examples completed!"
echo "======================================"
echo ""
echo "Generated files:"
ls -lh example_*.wav 2>/dev/null || echo "No files generated"
echo ""
echo "To play the audio files:"
echo "  Linux:   aplay example_1.wav"
echo "  macOS:   afplay example_1.wav"
echo "  Windows: start example_1.wav"
