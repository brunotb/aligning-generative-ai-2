"""
Central configuration for the voice API package.

Configuration includes:
- Logging setup (level, format)
- Model selection and parameters
- Audio capture/playback settings

Settings can be controlled via environment variables:
- APP_LOG_LEVEL: Logging level (default: INFO)
- APP_MODEL_NAME: Gemini model name (default: gemini-2.5-flash-native-audio-preview-09-2025)

Note: System prompts have been moved to voice_api.llm.prompts (single source of truth).
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_LEVEL = os.getenv("APP_LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="[%(levelname)s] %(name)s - %(message)s",
)
LOGGER = logging.getLogger("voice_api")

# ---------------------------------------------------------------------------
# Model configuration
# ---------------------------------------------------------------------------
MODEL_NAME = os.getenv("APP_MODEL_NAME", "gemini-2.5-flash-native-audio-preview-09-2025")

# ---------------------------------------------------------------------------
# Audio configuration
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AudioConfig:
    """
    Audio parameters for both capture and playback.

    Attributes:
        format: PyAudio format code (paInt16 for 16-bit PCM)
        channels: Number of audio channels (1 for mono)
        send_sample_rate: Microphone sample rate (16000 Hz recommended)
        receive_sample_rate: Speaker sample rate (24000 Hz for Gemini Live)
        chunk_size: Audio frame size (1024 bytes typical)
        mic_queue_maxsize: Maximum pending microphone chunks (prevents memory buildup)
    """

    format: int
    channels: int
    send_sample_rate: int
    receive_sample_rate: int
    chunk_size: int
    mic_queue_maxsize: int = 5


def default_audio_config() -> AudioConfig:
    """
    Return default audio configuration for Gemini Live.

    Uses standard settings for voice communication:
    - 16-bit PCM mono audio
    - 16000 Hz for microphone (compatible with speech recognition)
    - 24000 Hz for speaker (Gemini Live output rate)
    - 1024-byte chunks (standard frame size)

    Returns:
        AudioConfig with sensible defaults

    Raises:
        ImportError: If PyAudio cannot be imported
    """
    import pyaudio  # Lazy import to keep module load lightweight

    return AudioConfig(
        format=pyaudio.paInt16,
        channels=1,
        send_sample_rate=16000,
        receive_sample_rate=24000,
        chunk_size=1024,
    )
