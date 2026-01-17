"""
Voice pipeline runner that can be controlled via REST API.

This module allows starting/stopping the voice pipeline programmatically,
enabling integration with the web frontend.
"""

from __future__ import annotations

import asyncio
import threading
from typing import Optional

from ..client import run as run_voice_client
from ..config import LOGGER


class VoicePipelineRunner:
    """
    Manages the voice pipeline lifecycle.
    
    Allows starting and stopping the voice pipeline in a separate thread,
    enabling REST API control.
    """
    
    def __init__(self) -> None:
        """Initialize the runner."""
        self._thread: Optional[threading.Thread] = None
        self._stop_event: Optional[asyncio.Event] = None
        self._is_running = False
        self._current_session_id: Optional[str] = None
    
    def start(self, session_id: str = "default") -> bool:
        """
        Start the voice pipeline in a background thread.
        
        Args:
            session_id: Session identifier for this voice session
            
        Returns:
            True if started successfully, False if already running
        """
        if self._is_running:
            LOGGER.warning("Voice pipeline already running")
            return False
        
        self._current_session_id = session_id
        
        def run_in_thread():
            try:
                asyncio.run(run_voice_client())
            except KeyboardInterrupt:
                LOGGER.info("Voice pipeline interrupted")
            except Exception as e:
                LOGGER.error("Voice pipeline error: %s", e)
            finally:
                self._is_running = False
                self._current_session_id = None
        
        self._thread = threading.Thread(target=run_in_thread, daemon=True)
        self._thread.start()
        self._is_running = True
        
        LOGGER.info("Voice pipeline started for session: %s", session_id)
        return True
    
    def get_current_session_id(self) -> Optional[str]:
        """
        Get the current session ID.
        
        Returns:
            Current session ID or None
        """
        return self._current_session_id
    
    def stop(self) -> bool:
        """
        Stop the voice pipeline.
        
        Returns:
            True if stopped successfully, False if not running
        """
        if not self._is_running:
            LOGGER.warning("Voice pipeline not running")
            return False
        
        # Note: Stopping is tricky because the voice client runs in asyncio
        # For now, we rely on the thread being daemon and terminating naturally
        # A more sophisticated implementation would use a stop event
        
        self._is_running = False
        LOGGER.info("Voice pipeline stop requested")
        return True
    
    def is_running(self) -> bool:
        """
        Check if voice pipeline is running.
        
        Returns:
            True if running, False otherwise
        """
        return self._is_running


# Global singleton instance
voice_runner = VoicePipelineRunner()
