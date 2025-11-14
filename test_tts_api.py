#!/usr/bin/env python3
"""
Test script for the GGUF TTS API Server

Usage:
    python test_tts_api.py [--url URL]

This script tests the TTS API endpoints to ensure they're working correctly.
"""

import argparse
import requests
import sys
import json


def test_root(base_url):
    """Test the root endpoint"""
    print("\n" + "="*60)
    print("Testing Root Endpoint")
    print("="*60)
    
    try:
        response = requests.get(f"{base_url}/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_health(base_url):
    """Test the health check endpoint"""
    print("\n" + "="*60)
    print("Testing Health Endpoint")
    print("="*60)
    
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_models(base_url):
    """Test the models list endpoint"""
    print("\n" + "="*60)
    print("Testing Models Endpoint")
    print("="*60)
    
    try:
        response = requests.get(f"{base_url}/v1/models")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_tts(base_url, output_file="test_output.wav"):
    """Test the TTS generation endpoint"""
    print("\n" + "="*60)
    print("Testing TTS Generation Endpoint")
    print("="*60)
    
    try:
        payload = {
            "model": "vibevoice",
            "input": "Hello! This is a test of the text to speech system. How are you today?",
            "voice": "alloy",
            "speed": 1.0
        }
        
        print(f"Request payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(
            f"{base_url}/v1/audio/speech",
            json=payload,
            timeout=120  # TTS generation can take time
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            # Save the audio file
            with open(output_file, "wb") as f:
                f.write(response.content)
            print(f"Audio saved to: {output_file}")
            print(f"Audio size: {len(response.content)} bytes")
            return True
        else:
            print(f"Error response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Test GGUF TTS API Server")
    parser.add_argument(
        "--url",
        type=str,
        default="http://localhost:8000",
        help="Base URL of the TTS API server (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--skip-tts",
        action="store_true",
        help="Skip the TTS generation test (useful if model not loaded)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="test_output.wav",
        help="Output file for TTS test (default: test_output.wav)"
    )
    
    args = parser.parse_args()
    
    print("="*60)
    print("GGUF TTS API Server Test Suite")
    print("="*60)
    print(f"Target URL: {args.url}")
    
    results = {}
    
    # Test each endpoint
    results["root"] = test_root(args.url)
    results["health"] = test_health(args.url)
    results["models"] = test_models(args.url)
    
    if not args.skip_tts:
        results["tts"] = test_tts(args.url, args.output)
    else:
        print("\nSkipping TTS generation test")
        results["tts"] = None
    
    # Print summary
    print("\n" + "="*60)
    print("Test Results Summary")
    print("="*60)
    
    for test_name, result in results.items():
        if result is None:
            status = "SKIPPED"
        elif result:
            status = "✅ PASSED"
        else:
            status = "❌ FAILED"
        print(f"{test_name.upper()}: {status}")
    
    # Determine overall result
    passed = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)
    skipped = sum(1 for r in results.values() if r is None)
    
    print(f"\nTotal: {passed} passed, {failed} failed, {skipped} skipped")
    
    if failed > 0:
        print("\n⚠️  Some tests failed. Please check the server logs.")
        sys.exit(1)
    else:
        print("\n✅ All tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
