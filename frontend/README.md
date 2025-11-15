# GGUF Connector - Futuristic Frontend

A modern, cyberpunk-inspired web interface for the GGUF Connector project, providing a unified dashboard for all AI model operations.

## Features

### 🤖 **AI Chat Interface**
- Interactive chat with GGUF language models
- Support for multiple models (Llama, Mistral, Vicuna, etc.)
- Real-time streaming responses
- Beautiful message history

### 🎨 **Image Generation**
- Text-to-image generation with Flux, Stable Diffusion 3.5, PixArt, and Lumina
- Configurable parameters (width, height, steps, guidance)
- Live preview and download
- Multiple model support

### ✏️ **Image Editor**
- AI-powered image editing with Kontext
- Upload and edit existing images
- Natural language instructions
- Adjustable guidance scale

### 🎙️ **Text-to-Speech**
- Convert text to natural speech
- Multiple voice models (VibeVoice, Dia, Higgs)
- Voice selection (Alloy, Echo, Fable, Onyx, Nova, Shimmer)
- Adjustable speech speed

### 🛠️ **GGUF Tools**
- Convert between GGUF and SafeTensors
- Quantize models
- Merge and split files
- Metadata inspection
- Tensor operations

### 📚 **Model Management**
- Browse available GGUF models
- View model information
- Easy model selection

## Design Features

- **Futuristic Cyberpunk Aesthetic**: Neon colors, glassmorphism, and glowing effects
- **Animated Background**: Dynamic grid and particle effects
- **Smooth Transitions**: Fluid animations throughout
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Dark Theme**: Easy on the eyes for extended use
- **Custom Fonts**: Orbitron and Rajdhani for that sci-fi feel

## Quick Start

### Run the Frontend

From the repository root:

```bash
python run_frontend.py
```

This will:
1. Start a local web server on port 5173
2. Automatically open your browser
3. Serve the futuristic frontend interface

### Run with Backend API

For full functionality, run the backend services:

```bash
# Terminal 1: Start the TTS API server (if needed)
python run_tts_server.py

# Terminal 2: Start the frontend
python run_frontend.py
```

## File Structure

```
frontend/
├── index.html      # Main HTML structure
├── style.css       # Futuristic styling and animations
├── script.js       # Interactive functionality
└── README.md       # This file
```

## Customization

### Colors

Edit `style.css` to customize the color scheme:

```css
:root {
    --primary-cyan: #00c3ff;
    --primary-green: #00ff88;
    --primary-purple: #bd00ff;
    --primary-pink: #ff006e;
}
```

### Layout

The interface uses CSS Grid for responsive layouts. Adjust breakpoints in `style.css`:

```css
@media (max-width: 768px) {
    /* Mobile styles */
}
```

## Integration with Backend

The frontend is designed to integrate with GGUF Connector's existing functionality:

- **Chat**: Connects to ctransformers or llama.cpp backends
- **Image Generation**: Interfaces with Gradio-based image generators
- **TTS**: Uses the OpenAI-compatible TTS API server
- **Tools**: Executes GGUF conversion and manipulation tools

### API Endpoints (To Be Implemented)

```javascript
// Chat
POST /api/chat
{ "model": "model.gguf", "message": "Hello!" }

// Image Generation
POST /api/generate-image
{ "model": "flux", "prompt": "...", "width": 1024, "height": 1024 }

// Image Editing
POST /api/edit-image
{ "image": "base64...", "instruction": "..." }

// TTS
POST /api/tts
{ "model": "vibevoice", "text": "...", "voice": "alloy" }
```

## Browser Support

- Chrome/Edge (Recommended)
- Firefox
- Safari
- Opera

## Performance

- Lightweight: ~55KB total (HTML + CSS + JS)
- Fast loading: < 1 second on most connections
- Smooth animations: 60 FPS on modern hardware
- Responsive: Optimized for all screen sizes

## Future Enhancements

- [ ] Real-time model loading progress
- [ ] Batch image generation
- [ ] Video generation interface
- [ ] Advanced model parameters
- [ ] User preferences and themes
- [ ] Model download manager
- [ ] Performance metrics dashboard
- [ ] Multi-language support

## Credits

- **Design**: Inspired by cyberpunk and sci-fi aesthetics
- **Fonts**: Google Fonts (Orbitron, Rajdhani)
- **Icons**: Feather Icons (embedded as SVG)

## License

Part of the GGUF Connector project.
