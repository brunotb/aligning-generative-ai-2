"""
FastAPI web server for voice form assistant.

Provides WebSocket and REST endpoints for frontend integration.
"""

from .events import EventEmitter, event_emitter
from .server import app

__all__ = ["app", "EventEmitter", "event_emitter"]
