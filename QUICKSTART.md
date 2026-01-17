# Quick Start Guide

## Instant Setup (3 steps)

### 1. Install Backend Dependencies
```powershell
pip install -r requirements.txt
```

### 2. Install Frontend Dependencies
```powershell
cd frontend
npm install
cd ..
```

### 3. Set API Key & Run
```powershell
# Set your Google API key
$env:GOOGLE_API_KEY = "your-gemini-api-key-here"

# Start everything
.\start_app_full.ps1
```

The application will open at: **http://localhost:5173**

## What You'll See

1. **Welcome Screen** - Click "Start Conversation" to begin
2. **Conversation Screen**:
   - Left (2/3): Animated microphone indicator
   - Right (1/3): Form fields with progress bar
3. **Voice Interaction**: Speak naturally to fill the form
4. **PDF Generation**: Click "Print PDF" anytime to download

## Architecture Overview

```
User speaks → Microphone → Python (PyAudio) → Gemini Live API
                                                      ↓
                                              AI processes & validates
                                                      ↓
React UI ← WebSocket ← FastAPI ← Event Emitter ← Voice Pipeline
```

## Troubleshooting

**Frontend won't start?**
```powershell
cd frontend
rm -rf node_modules
npm install
npm run dev
```

**Backend errors?**
```powershell
pip install --upgrade -r requirements.txt
```

**No microphone detected?**
- Check Windows microphone permissions
- Verify PyAudio installed: `python -c "import pyaudio"`

## Tech Stack Summary

- **Backend**: Python 3.10+, FastAPI, Google Gemini Live
- **Frontend**: React 18, TypeScript, Tailwind CSS, Zustand
- **Real-time**: WebSockets for bidirectional updates
- **Audio**: PyAudio for native microphone access

Enjoy! 🎤
