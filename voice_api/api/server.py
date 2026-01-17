"""
FastAPI application with WebSocket and REST endpoints.

Provides:
- WebSocket: Real-time form state updates
- REST: Session management, field editing, PDF generation
"""

from __future__ import annotations

import asyncio
import json
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from ..app.state import FormState
from ..app.validation import validate_field
from ..config import LOGGER
from ..core import ANMELDUNG_FORM_FIELDS, FIELD_BY_ID, generate_anmeldung_pdf
from .events import FormEvent, event_emitter
from .voice_runner import voice_runner


# Session storage (in-memory for simplicity, use Redis for production)
sessions: Dict[str, FormState] = {}


async def sync_form_state_from_events(event: FormEvent):
    """
    Sync server's form_state from voice pipeline events.
    
    This listener ensures that when the voice pipeline saves fields,
    the server's session storage is updated so PDF generation works.
    """
    session_id = event.session_id
    if session_id not in sessions:
        LOGGER.warning("Event received for unknown session: %s", session_id)
        return
    
    form_state = sessions[session_id]
    
    if event.type == "field_saved":
        # Update the server's form_state with the saved value
        field_id = event.data.get("field_id")
        value = event.data.get("value")
        
        if field_id and value is not None:
            # Record the value and advance if not already at this position
            form_state.record_value(field_id, value)
            
            # Advance to next field if we're still on this field
            current_field = form_state.current_field()
            if current_field and current_field.field_id == field_id:
                form_state.advance()
            
            LOGGER.info(
                "Synced field %s=%s to server session %s (progress: %.1f%%, total answers: %d)",
                field_id,
                value,
                session_id,
                form_state.progress_percent(),
                len(form_state.answers),
            )
        else:
            LOGGER.warning("field_saved event missing field_id or value: %s", event.data)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the FastAPI app."""
    LOGGER.info("Starting FastAPI server")
    
    # Subscribe to events to sync form state
    await event_emitter.subscribe(sync_form_state_from_events)
    LOGGER.info("Subscribed to form events for state synchronization")
    
    yield
    
    LOGGER.info("Shutting down FastAPI server")


app = FastAPI(
    title="Voice Form Assistant API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Request/Response Models
# ============================================================================


class SessionCreateResponse(BaseModel):
    """Response for session creation."""
    session_id: str
    message: str


class FieldUpdateRequest(BaseModel):
    """Request to update a field value."""
    value: str


class FieldUpdateResponse(BaseModel):
    """Response for field update."""
    ok: bool
    is_valid: bool
    message: str


class SessionStatusResponse(BaseModel):
    """Current session status."""
    session_id: str
    current_index: int
    total_fields: int
    progress_percent: float
    is_complete: bool
    current_field: Optional[Dict[str, Any]]
    answers: Dict[str, str]


# ============================================================================
# REST Endpoints
# ============================================================================


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "voice-form-assistant"}


@app.post("/api/session/start", response_model=SessionCreateResponse)
async def start_session():
    """
    Create a new form session and start voice pipeline.
    
    Returns:
        SessionCreateResponse with session_id
    """
    session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    sessions[session_id] = FormState()
    
    LOGGER.info("Created session: %s", session_id)
    
    # Start voice pipeline
    voice_runner.start(session_id)
    
    # Emit session started event
    await event_emitter.emit(
        FormEvent(
            type="session_started",
            data={
                "session_id": session_id,
                "total_fields": len(ANMELDUNG_FORM_FIELDS),
            },
            session_id=session_id,
        )
    )
    
    return SessionCreateResponse(
        session_id=session_id,
        message="Session created successfully",
    )


@app.get("/api/session/{session_id}/status", response_model=SessionStatusResponse)
async def get_session_status(session_id: str):
    """
    Get current session status.
    
    Args:
        session_id: Session identifier
        
    Returns:
        SessionStatusResponse with current state
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    form_state = sessions[session_id]
    current_field = form_state.current_field()
    
    return SessionStatusResponse(
        session_id=session_id,
        current_index=form_state.current_index,
        total_fields=len(form_state.fields),
        progress_percent=form_state.progress_percent(),
        is_complete=form_state.is_complete(),
        current_field={
            "field_id": current_field.field_id,
            "label": current_field.label,
            "description": current_field.description,
            "examples": current_field.examples,
        } if current_field else None,
        answers=form_state.answers,
    )


@app.put(
    "/api/session/{session_id}/field/{field_id}",
    response_model=FieldUpdateResponse,
)
async def update_field(session_id: str, field_id: str, request: FieldUpdateRequest):
    """
    Manually update a field value (for user edits in UI).
    
    Args:
        session_id: Session identifier
        field_id: Field identifier
        request: Field update request with new value
        
    Returns:
        FieldUpdateResponse with validation result
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    field = FIELD_BY_ID.get(field_id)
    if not field:
        raise HTTPException(status_code=404, detail=f"Field {field_id} not found")
    
    form_state = sessions[session_id]
    
    # Validate the new value
    is_valid, message = validate_field(field, request.value)
    
    if is_valid:
        form_state.record_value(field_id, request.value)
        
        # Emit field updated event
        await event_emitter.emit(
            FormEvent(
                type="field_updated",
                data={
                    "field_id": field_id,
                    "value": request.value,
                    "progress_percent": form_state.progress_percent(),
                },
                session_id=session_id,
            )
        )
        
        return FieldUpdateResponse(
            ok=True,
            is_valid=True,
            message="Field updated successfully",
        )
    else:
        return FieldUpdateResponse(
            ok=False,
            is_valid=False,
            message=message,
        )


@app.get("/api/session/{session_id}/pdf")
async def download_pdf(session_id: str):
    """
    Generate and download the filled PDF.
    
    Args:
        session_id: Session identifier
        
    Returns:
        PDF file response
    """
    if session_id not in sessions:
        LOGGER.error("PDF requested for unknown session: %s", session_id)
        raise HTTPException(status_code=404, detail="Session not found")
    
    form_state = sessions[session_id]
    
    LOGGER.info(
        "PDF generation requested for session %s: %d answers collected",
        session_id,
        len(form_state.answers),
    )
    
    if not form_state.answers:
        LOGGER.warning(
            "No form data available for PDF generation in session %s. "
            "Available sessions: %s",
            session_id,
            list(sessions.keys()),
        )
        raise HTTPException(
            status_code=400,
            detail=f"No form data to generate PDF. Please fill out at least one field before generating the PDF.",
        )
    
    try:
        LOGGER.debug("Generating PDF with answers: %s", form_state.answers)
        
        # Generate PDF
        pdf_bytes = generate_anmeldung_pdf(form_state.answers)
        
        # Save to output folder
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"anmeldung_{session_id}_{timestamp}.pdf"
        output_path = os.path.join(output_dir, output_filename)
        
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)
        
        LOGGER.info("PDF generated successfully: %s (%d bytes)", output_path, len(pdf_bytes))
        
        # Return file
        return FileResponse(
            path=output_path,
            media_type="application/pdf",
            filename=f"anmeldung_{timestamp}.pdf",
        )
    
    except Exception as e:
        LOGGER.error("PDF generation failed for session %s: %s", session_id, e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"PDF generation failed: {str(e)}",
        )


@app.delete("/api/session/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Success message
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    del sessions[session_id]
    LOGGER.info("Deleted session: %s", session_id)
    
    return {"message": "Session deleted successfully"}


# ============================================================================
# WebSocket Endpoint
# ============================================================================


@app.websocket("/api/session/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time form state updates.
    
    Clients connect here to receive events about field changes,
    validation results, transcripts, and progress updates.
    
    Args:
        websocket: WebSocket connection
        session_id: Session identifier
    """
    await websocket.accept()
    LOGGER.info("WebSocket connected: %s", session_id)
    
    # Create queue for this connection
    queue: asyncio.Queue = asyncio.Queue()
    await event_emitter.subscribe(queue)
    
    try:
        # Send initial state
        if session_id in sessions:
            form_state = sessions[session_id]
            current_field = form_state.current_field()
            
            await websocket.send_json({
                "type": "initial_state",
                "data": {
                    "fields": [
                        {
                            "field_id": f.field_id,
                            "label": f.label,
                            "description": f.description,
                            "examples": f.examples,
                            "required": f.required,
                            "validator_type": f.validator.type,
                            "enum_values": f.enum_values,
                        }
                        for f in ANMELDUNG_FORM_FIELDS
                    ],
                    "current_index": form_state.current_index,
                    "answers": form_state.answers,
                    "progress_percent": form_state.progress_percent(),
                },
            })
        
        # Listen for events and forward to client
        while True:
            # Wait for event with timeout to allow checking connection
            try:
                event = await asyncio.wait_for(queue.get(), timeout=1.0)
                
                # Only send events for this session (or broadcast events)
                if event.session_id == session_id or event.session_id == "broadcast":
                    await websocket.send_json({
                        "type": event.type,
                        "data": event.data,
                    })
            
            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                try:
                    await websocket.send_json({"type": "ping"})
                except:
                    break
    
    except WebSocketDisconnect:
        LOGGER.info("WebSocket disconnected: %s", session_id)
    
    except Exception as e:
        LOGGER.error("WebSocket error: %s", e)
    
    finally:
        await event_emitter.unsubscribe(queue)


# ============================================================================
# Session Management for Voice Pipeline
# ============================================================================


def get_or_create_session(session_id: str = "default") -> FormState:
    """
    Get existing session or create a new one.
    
    This is called by the voice pipeline to get the form state.
    
    Args:
        session_id: Session identifier
        
    Returns:
        FormState instance
    """
    if session_id not in sessions:
        sessions[session_id] = FormState()
        LOGGER.info("Auto-created session: %s", session_id)
    
    return sessions[session_id]
