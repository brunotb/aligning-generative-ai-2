# Voice Form Assistant - Setup Guide

## Project Overview

This is a voice-powered form assistant that helps users complete Munich residence registration (Anmeldung) forms through natural conversation using Google Gemini Live AI.

## Architecture

- **Backend**: Python + FastAPI + Google Gemini Live API
- **Frontend**: React + TypeScript + Tailwind CSS + Zustand
- **Communication**: WebSocket for real-time updates + REST API

## Prerequisites

1. **Python 3.10+** with pip
2. **Node.js 18+** with npm
3. **Google API Key** for Gemini API
4. **PyAudio dependencies** (Windows: included with PyAudio wheel)

## Setup Instructions

### 1. Backend Setup

```powershell
# Install Python dependencies
pip install -r requirements.txt

# Set your Google API key
$env:GOOGLE_API_KEY = "your-api-key-here"
```

### 2. Frontend Setup

```powershell
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Return to root
cd ..
```

### 3. Running the Application

#### Option A: Using the startup script (Recommended)

```powershell
.\start_app_full.ps1
```

This will:
- Start the FastAPI backend on `http://localhost:8001`
- Start the Vite frontend on `http://localhost:5173`
- Open your browser automatically

#### Option B: Manual startup

**Terminal 1 - Backend:**
```powershell
uvicorn voice_api.api.server:app --host 0.0.0.0 --port 8001 --reload
```

**Terminal 2 - Voice Pipeline (when ready to start conversation):**
```powershell
python -m voice_api.client
```

**Terminal 3 - Frontend:**
```powershell
cd frontend
npm run dev
```

### 4. Using the Application

1. Open `http://localhost:5173` in your browser
2. Click **"Start Conversation"** on the welcome screen
3. The voice pipeline will automatically begin
4. Speak naturally to answer questions
5. Monitor progress and edit fields in the right panel
6. Click **"Print PDF"** anytime to download your form

## Project Structure

```
aligning-generative-ai/
├── voice_api/              # Python backend
│   ├── api/               # FastAPI server & WebSocket
│   │   ├── server.py     # Main API routes
│   │   ├── events.py     # Event emitter
│   │   └── __init__.py
│   ├── app/               # Voice pipeline
│   │   ├── session.py    # Audio streaming
│   │   ├── state.py      # Form state
│   │   └── audio.py      # PyAudio helpers
│   ├── core/              # Business logic
│   │   ├── fields.py     # Form definitions
│   │   ├── validators.py # Field validation
│   │   └── pdf_generator.py
│   ├── llm/               # AI integration
│   │   ├── handlers.py   # Tool call handlers
│   │   ├── prompts.py    # System prompts
│   │   └── tools.py      # Tool definitions
│   └── client.py          # Voice client entry point
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/   # React components
│   │   │   ├── WelcomeScreen.tsx
│   │   │   ├── ConversationScreen.tsx
│   │   │   ├── MicrophoneIndicator.tsx
│   │   │   ├── FormFieldList.tsx
│   │   │   ├── ProgressBar.tsx
│   │   │   └── PrintPDFButton.tsx
│   │   ├── hooks/        # Custom hooks
│   │   │   └── useWebSocket.ts
│   │   ├── store/        # State management
│   │   │   └── formStore.ts
│   │   ├── types/        # TypeScript types
│   │   │   └── form.ts
│   │   ├── services/     # API client
│   │   │   └── api.ts
│   │   ├── App.tsx       # Main app component
│   │   └── main.tsx      # Entry point
│   └── package.json
├── documents/             # PDF template
├── output/                # Generated PDFs
└── requirements.txt
```

## API Endpoints

### REST API

- `POST /api/session/start` - Create new session
- `GET /api/session/{id}/status` - Get session status
- `PUT /api/session/{id}/field/{field_id}` - Update field manually
- `GET /api/session/{id}/pdf` - Download PDF
- `DELETE /api/session/{id}` - Delete session

### WebSocket

- `WS /api/session/ws/{session_id}` - Real-time updates

WebSocket events:
- `initial_state` - Initial form state
- `field_changed` - Current field changed
- `validation_result` - Validation feedback
- `field_saved` - Field successfully saved
- `transcript` - User/assistant speech
- `form_complete` - Form completed

## Troubleshooting

### PyAudio Installation Issues (Windows)

If pip fails to install PyAudio, download the appropriate wheel from:
https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

Then install:
```powershell
pip install PyAudio‑0.2.13‑cp310‑cp310‑win_amd64.whl
```

### WebSocket Connection Issues

- Ensure backend is running on port 8001
- Check firewall settings
- Verify CORS configuration in server.py

### Voice Pipeline Not Starting

- Verify GOOGLE_API_KEY environment variable is set
- Check microphone permissions
- Ensure PyAudio is properly installed

## Development

### Frontend Development

```powershell
cd frontend
npm run dev    # Start dev server
npm run build  # Build for production
npm run preview # Preview production build
```

### Backend Development

```powershell
# Run with auto-reload
uvicorn voice_api.api.server:app --reload --port 8001

# Run tests
pytest
```

## Production Deployment

### Frontend (Vercel)

The frontend is already configured for Vercel deployment with `vercel.json`.

```powershell
cd frontend
npm run build
# Deploy dist/ folder to Vercel
```

### Backend

Deploy to:
- **Railway**: One-click deployment
- **Fly.io**: Supports WebSockets
- **Cloud Run**: Requires WebSocket configuration

## License

MIT License - See LICENSE file for details

## Support

For issues or questions, please open an issue on GitHub.
