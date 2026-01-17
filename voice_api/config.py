"""Central configuration for the voice API package."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_LEVEL = os.getenv("APP_LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="[%(levelname)s] %(name)s - %(message)s",
    # format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
LOGGER = logging.getLogger("voice_api")

# ---------------------------------------------------------------------------
# Model and prompt configuration
# ---------------------------------------------------------------------------
MODEL_NAME = os.getenv("APP_MODEL_NAME", "gemini-2.5-flash-native-audio-preview-09-2025")

SYSTEM_PROMPT_BASE = (
    "You are a helpful assistant guiding a user through completing a form.\n"
    "Always follow this loop: welcome -> get_next_form_field -> explain field -> "
    "collect user reply -> validate_form_field -> if invalid, explain and ask again; "
    "if valid, save_form_field and give validation to user-> get_next_form_field -> repeat until done.\n"
    "Speak concisely, one question at a time. Reflect validation errors back with a short reason."
    "Use the tools provided to get and save form fields. And ensure a good user experience.\n"
    "Welcome the user directly without waiting for them to say hello first.\n"
)

# ---------------------------------------------------------------------------
# Audio configuration
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AudioConfig:
    """Audio parameters for both capture and playback."""

    format: int
    channels: int
    send_sample_rate: int
    receive_sample_rate: int
    chunk_size: int
    mic_queue_maxsize: int = 5


def default_audio_config() -> AudioConfig:
    """Return default audio settings (pyaudio constants imported lazily)."""
    import pyaudio  # Lazy import to keep module load light

    return AudioConfig(
        format=pyaudio.paInt16,
        channels=1,
        send_sample_rate=16000,
        receive_sample_rate=24000,
        chunk_size=1024,
    )
