// Global state
const state = {
    currentSection: 'chat',
    models: [],
    chatHistory: [],
    currentImage: null,
    currentAudio: null
};

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    initializeNavigation();
    initializeParticles();
    initializeSliders();
    initializeChat();
    initializeImageGeneration();
    initializeImageEditor();
    initializeTTS();
    loadModels();
});

// Navigation
function initializeNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    const sections = document.querySelectorAll('.section');
    
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const targetSection = item.dataset.section;
            
            // Update nav items
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');
            
            // Update sections
            sections.forEach(section => section.classList.remove('active'));
            document.getElementById(targetSection).classList.add('active');
            
            state.currentSection = targetSection;
        });
    });
}

// Animated particles
function initializeParticles() {
    const particlesContainer = document.getElementById('particles');
    const particleCount = 50;
    
    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.style.position = 'absolute';
        particle.style.width = Math.random() * 3 + 'px';
        particle.style.height = particle.style.width;
        particle.style.background = `rgba(0, ${Math.random() * 255}, 255, ${Math.random() * 0.5})`;
        particle.style.borderRadius = '50%';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.top = Math.random() * 100 + '%';
        particle.style.animation = `float ${Math.random() * 10 + 5}s infinite ease-in-out`;
        particle.style.animationDelay = Math.random() * 5 + 's';
        particlesContainer.appendChild(particle);
    }
}

// Slider value updates
function initializeSliders() {
    const sliders = [
        { id: 'imageSteps', valueId: 'stepsValue' },
        { id: 'imageGuidance', valueId: 'guidanceValue' },
        { id: 'editorGuidance', valueId: 'editorGuidanceValue' },
        { id: 'ttsSpeed', valueId: 'ttsSpeedValue' }
    ];
    
    sliders.forEach(({ id, valueId }) => {
        const slider = document.getElementById(id);
        const valueDisplay = document.getElementById(valueId);
        
        if (slider && valueDisplay) {
            slider.addEventListener('input', (e) => {
                valueDisplay.textContent = e.target.value;
            });
        }
    });
}

// Chat functionality
function initializeChat() {
    const chatInput = document.getElementById('chatInput');
    const chatSend = document.getElementById('chatSend');
    const chatMessages = document.getElementById('chatMessages');
    
    // Auto-resize textarea
    chatInput.addEventListener('input', (e) => {
        e.target.style.height = 'auto';
        e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
    });
    
    // Send message
    const sendMessage = () => {
        const message = chatInput.value.trim();
        const selectedModel = document.getElementById('chatModel').value;
        
        if (!message) return;
        
        if (!selectedModel) {
            showNotification('Please select a model first', 'warning');
            return;
        }
        
        // Clear welcome message if present
        const welcomeMessage = chatMessages.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }
        
        // Add user message
        addChatMessage(message, 'user');
        chatInput.value = '';
        chatInput.style.height = 'auto';
        
        // Simulate AI response (replace with actual API call)
        showLoading();
        setTimeout(() => {
            hideLoading();
            addChatMessage('This is a demo response. Connect to a GGUF model backend to get real responses.', 'assistant');
        }, 1500);
    };
    
    chatSend.addEventListener('click', sendMessage);
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
}

function addChatMessage(content, role) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = content;
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    state.chatHistory.push({ role, content });
}

// Image Generation
function initializeImageGeneration() {
    const generateBtn = document.getElementById('generateImage');
    const downloadBtn = document.getElementById('downloadImage');
    
    generateBtn.addEventListener('click', async () => {
        const prompt = document.getElementById('imagePrompt').value.trim();
        
        if (!prompt) {
            showNotification('Please enter a prompt', 'warning');
            return;
        }
        
        const params = {
            model: document.getElementById('imageModel').value,
            prompt: prompt,
            width: parseInt(document.getElementById('imageWidth').value),
            height: parseInt(document.getElementById('imageHeight').value),
            steps: parseInt(document.getElementById('imageSteps').value),
            guidance: parseFloat(document.getElementById('imageGuidance').value)
        };
        
        showLoading();
        
        // Simulate image generation (replace with actual API call)
        setTimeout(() => {
            hideLoading();
            displayGeneratedImage('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNTAwIiBoZWlnaHQ9IjUwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iNTAwIiBoZWlnaHQ9IjUwMCIgZmlsbD0iIzFhMjAzMyIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LXNpemU9IjI0IiBmaWxsPSIjMDBjM2ZmIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkb21pbmFudC1iYXNlbGluZT0ibWlkZGxlIj5EZW1vIEltYWdlPC90ZXh0Pjwvc3ZnPg==');
            showNotification('Image generated successfully!', 'success');
        }, 2000);
    });
    
    downloadBtn.addEventListener('click', () => {
        if (state.currentImage) {
            const link = document.createElement('a');
            link.href = state.currentImage;
            link.download = 'generated-image.png';
            link.click();
        }
    });
}

function displayGeneratedImage(imageData) {
    const preview = document.getElementById('imagePreview');
    preview.innerHTML = '';
    
    const img = document.createElement('img');
    img.src = imageData;
    img.className = 'generated-image';
    preview.appendChild(img);
    
    state.currentImage = imageData;
    document.getElementById('downloadImage').disabled = false;
}

// Image Editor
function initializeImageEditor() {
    const uploadInput = document.getElementById('editorImageUpload');
    const applyBtn = document.getElementById('applyEdit');
    
    uploadInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (event) => {
                displayEditorImage(event.target.result);
                applyBtn.disabled = false;
            };
            reader.readAsDataURL(file);
        }
    });
    
    applyBtn.addEventListener('click', () => {
        const instruction = document.getElementById('editorPrompt').value.trim();
        
        if (!instruction) {
            showNotification('Please enter an edit instruction', 'warning');
            return;
        }
        
        showLoading();
        
        // Simulate image editing (replace with actual API call)
        setTimeout(() => {
            hideLoading();
            showNotification('Edit applied successfully!', 'success');
        }, 2000);
    });
}

function displayEditorImage(imageData) {
    const preview = document.getElementById('editorPreview');
    preview.innerHTML = '';
    
    const img = document.createElement('img');
    img.src = imageData;
    img.className = 'generated-image';
    preview.appendChild(img);
}

// TTS
function initializeTTS() {
    const generateBtn = document.getElementById('generateSpeech');
    
    generateBtn.addEventListener('click', async () => {
        const text = document.getElementById('ttsText').value.trim();
        
        if (!text) {
            showNotification('Please enter text to speak', 'warning');
            return;
        }
        
        const params = {
            model: document.getElementById('ttsModel').value,
            voice: document.getElementById('ttsVoice').value,
            text: text,
            speed: parseFloat(document.getElementById('ttsSpeed').value)
        };
        
        showLoading();
        
        // Simulate TTS generation (replace with actual API call)
        setTimeout(() => {
            hideLoading();
            displayAudioPlayer();
            showNotification('Speech generated successfully!', 'success');
        }, 2000);
    });
}

function displayAudioPlayer() {
    const audioContainer = document.getElementById('audioPlayer');
    audioContainer.innerHTML = '';
    
    const audioWrapper = document.createElement('div');
    audioWrapper.style.width = '100%';
    audioWrapper.style.padding = '20px';
    
    const audio = document.createElement('audio');
    audio.controls = true;
    audio.style.width = '100%';
    audio.style.borderRadius = '8px';
    
    // Demo audio URL - replace with actual generated audio
    audio.src = 'data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA=';
    
    audioWrapper.appendChild(audio);
    audioContainer.appendChild(audioWrapper);
    
    const message = document.createElement('p');
    message.textContent = 'Audio generated (demo)';
    message.style.textAlign = 'center';
    message.style.marginTop = '15px';
    message.style.color = 'var(--text-secondary)';
    audioWrapper.appendChild(message);
}

// Load models
async function loadModels() {
    // Simulate loading models (replace with actual API call)
    const demoModels = [
        { name: 'llama-2-7b-chat.gguf', size: '3.8 GB' },
        { name: 'mistral-7b-instruct.gguf', size: '4.1 GB' },
        { name: 'vicuna-13b.gguf', size: '7.2 GB' }
    ];
    
    state.models = demoModels;
    
    // Populate chat model selector
    const chatModelSelect = document.getElementById('chatModel');
    demoModels.forEach(model => {
        const option = document.createElement('option');
        option.value = model.name;
        option.textContent = model.name;
        chatModelSelect.appendChild(option);
    });
    
    // Display models in models section
    displayModelsList(demoModels);
}

function displayModelsList(models) {
    const modelsList = document.getElementById('modelsList');
    
    if (models.length === 0) {
        return;
    }
    
    modelsList.innerHTML = '';
    
    models.forEach(model => {
        const card = document.createElement('div');
        card.className = 'model-card';
        
        const name = document.createElement('div');
        name.className = 'model-name';
        name.textContent = model.name;
        
        const size = document.createElement('div');
        size.className = 'model-size';
        size.textContent = `Size: ${model.size}`;
        
        card.appendChild(name);
        card.appendChild(size);
        modelsList.appendChild(card);
    });
}

// Loading overlay
function showLoading() {
    document.getElementById('loadingOverlay').classList.add('active');
}

function hideLoading() {
    document.getElementById('loadingOverlay').classList.remove('active');
}

// Notification system
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.padding = '15px 25px';
    notification.style.borderRadius = '10px';
    notification.style.zIndex = '10000';
    notification.style.animation = 'slideIn 0.3s ease';
    notification.style.fontFamily = 'var(--font-secondary)';
    notification.style.fontSize = '14px';
    notification.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.3)';
    
    // Set colors based on type
    switch (type) {
        case 'success':
            notification.style.background = 'rgba(0, 255, 136, 0.2)';
            notification.style.border = '1px solid var(--primary-green)';
            notification.style.color = 'var(--primary-green)';
            break;
        case 'warning':
            notification.style.background = 'rgba(255, 165, 0, 0.2)';
            notification.style.border = '1px solid orange';
            notification.style.color = 'orange';
            break;
        case 'error':
            notification.style.background = 'rgba(255, 0, 110, 0.2)';
            notification.style.border = '1px solid var(--primary-pink)';
            notification.style.color = 'var(--primary-pink)';
            break;
        default:
            notification.style.background = 'rgba(0, 195, 255, 0.2)';
            notification.style.border = '1px solid var(--primary-cyan)';
            notification.style.color = 'var(--primary-cyan)';
    }
    
    notification.textContent = message;
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Tool buttons
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('tool-button')) {
        showNotification('This tool is in demo mode. Connect to backend for full functionality.', 'info');
    }
});

// Status indicator animation
setInterval(() => {
    const statusDot = document.querySelector('.status-dot');
    if (statusDot) {
        statusDot.style.transform = statusDot.style.transform === 'scale(1.2)' ? 'scale(1)' : 'scale(1.2)';
    }
}, 1000);
