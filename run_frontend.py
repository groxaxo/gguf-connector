#!/usr/bin/env python3
"""
Futuristic Frontend Server for GGUF Connector
Serves the modern web interface and provides API endpoints for GGUF operations
"""

import os
import sys
import webbrowser
from pathlib import Path
import http.server
import socketserver
from functools import partial

def find_frontend_directory():
    """Find the frontend directory"""
    # Check multiple possible locations
    possible_paths = [
        Path(__file__).parent / "frontend",
        Path.cwd() / "frontend",
        Path(__file__).parent / "src" / "frontend"
    ]
    
    for path in possible_paths:
        if path.exists() and (path / "index.html").exists():
            return path
    
    print("Error: Frontend directory not found!")
    print("Please ensure the 'frontend' directory with index.html exists.")
    sys.exit(1)

def main():
    """Start the frontend server"""
    frontend_dir = find_frontend_directory()
    port = 5173
    
    # Custom handler to set CORS headers
    class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            super().end_headers()
        
        def do_OPTIONS(self):
            self.send_response(200)
            self.end_headers()
    
    # Create handler with the frontend directory
    Handler = partial(CORSRequestHandler, directory=str(frontend_dir))
    
    # Start server
    try:
        with socketserver.TCPServer(("", port), Handler) as httpd:
            url = f"http://localhost:{port}"
            print("=" * 60)
            print("🚀 GGUF Connector - Futuristic Frontend")
            print("=" * 60)
            print(f"Server running at: {url}")
            print(f"Serving from: {frontend_dir}")
            print("\nPress Ctrl+C to stop the server")
            print("=" * 60)
            
            # Open browser
            webbrowser.open(url)
            
            # Start serving
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n✨ Server stopped. Thank you for using GGUF Connector!")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\n❌ Error: Port {port} is already in use.")
            print("Please stop the other server or choose a different port.")
        else:
            print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
