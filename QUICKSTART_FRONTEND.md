# Quick Start Guide - Futuristic Frontend

Get started with the GGUF Connector futuristic web interface in just a few steps!

## Prerequisites

- Python 3.7 or higher
- A modern web browser (Chrome, Firefox, Safari, or Edge)

## Quick Start

### 1. Start the Frontend Server

From the repository root directory:

```bash
python run_frontend.py
```

That's it! The server will:
- Start on port 5173
- Automatically open your browser
- Display the futuristic interface

### 2. Explore the Interface

The frontend has 6 main sections accessible from the navigation bar:

#### 🤖 **CHAT AI**
- Select a GGUF language model
- Type your message
- Get AI responses

#### 🎨 **IMAGE GEN**
- Choose a model (Flux, SD 3.5, PixArt, Lumina)
- Enter a prompt
- Adjust parameters (width, height, steps, guidance)
- Click GENERATE
- Download your image

#### ✏️ **IMG EDIT**
- Upload an image
- Describe the changes you want
- Adjust guidance scale
- Apply the edit

#### 🎙️ **TTS**
- Select a voice model
- Choose a voice style
- Enter text to speak
- Adjust speed
- Generate and play audio

#### 🛠️ **TOOLS**
- Convert between formats
- Quantize models
- Merge/split files
- Inspect metadata

#### 📚 **MODELS**
- Browse available models
- View model information

## Demo Mode

The frontend currently runs in demo mode, which means:
- All UI features are functional
- Operations show loading animations and notifications
- No actual model processing occurs (returns placeholder data)

## Connect to Backend

To enable full functionality, you need to connect the frontend to GGUF Connector backends:

### For Text-to-Speech

1. Start the TTS server in a separate terminal:
```bash
python run_tts_server.py
```

2. The frontend will be able to connect to `http://localhost:8000`

### For Other Features

Backend integration is in progress. The frontend is designed to work with:
- ctransformers for chat
- Gradio-based image generators
- GGUF conversion tools
- Model management utilities

## Customization

### Change Port

Edit `run_frontend.py` and modify:
```python
port = 5173  # Change to your desired port
```

### Customize Colors

Edit `frontend/style.css` and modify the CSS variables:
```css
:root {
    --primary-cyan: #00c3ff;
    --primary-green: #00ff88;
    --primary-purple: #bd00ff;
    --primary-pink: #ff006e;
}
```

### Add Models

Models are automatically detected from the current directory. Place your `.gguf` files in the directory where you run the server.

## Troubleshooting

### Port Already in Use

If you see "Address already in use":
1. Stop any other servers running on port 5173
2. Or change the port in `run_frontend.py`

### Browser Doesn't Open

Manually navigate to: `http://localhost:5173`

### Fonts Not Loading

The interface uses Google Fonts. If you're offline or behind a firewall, the interface will fall back to system fonts.

## Tips

- **Responsive Design**: Try resizing your browser window - the interface adapts to any screen size
- **Keyboard Shortcuts**: Press Enter in the chat input to send messages
- **Smooth Scrolling**: The chat area auto-scrolls to show new messages
- **Visual Feedback**: Watch for loading animations and toast notifications

## Next Steps

1. **Explore All Sections**: Click through each navigation item
2. **Try Demo Features**: Test the interface in demo mode
3. **Connect Backends**: Set up backend services for full functionality
4. **Customize**: Modify colors and settings to your preference

## Support

For issues or questions:
- Check the main [README.md](README.md)
- Review [Frontend Documentation](frontend/README.md)
- Open an issue on GitHub

## What's Next?

Future enhancements planned:
- Full backend integration
- Real-time model loading progress
- Batch operations
- User preferences and themes
- Advanced model parameters
- Performance metrics dashboard

Enjoy the futuristic GGUF experience! 🚀
