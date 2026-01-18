"""
Audio pipeline helpers for microphone capture and playback.

Manages PyAudio streams and async queues for:
- Microphone input (capture user speech)
- Speaker output (playback model responses)

The AudioPipelines class wraps PyAudio and async queues into a convenient
context-aware object that handles stream lifecycle.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Optional
try:
    import pyaudio
except ImportError:
    pyaudio = None

from ..config import LOGGER, AudioConfig, default_audio_config


@dataclass
class AudioPipelines:
    """
    Wrap PyAudio input/output streams and async queues.

    Manages:
    - PyAudio streams for microphone and speaker
    - Async queues for decoupling capture/playback from model communication
    - Proper resource cleanup on close

    Attributes:
        config: AudioConfig with sample rates, chunk size, etc.
        pya_client: PyAudio instance for stream management
        mic_stream: Input stream from microphone
        speaker_stream: Output stream to speaker
        mic_queue: Async queue for microphone data
        playback_queue: Async queue for speaker data
    """

    config: AudioConfig = field(default_factory=default_audio_config)
    pya_client: Any = field(init=False, default=None)
    mic_stream: Any = None
    speaker_stream: Any = None
    mic_queue: asyncio.Queue = field(init=False)
    playback_queue: asyncio.Queue = field(init=False)

    def __post_init__(self) -> None:
        """Initialize async queues and PyAudio client after dataclass initialization."""
        self.mic_queue = asyncio.Queue(maxsize=self.config.mic_queue_maxsize)
        self.playback_queue = asyncio.Queue()
        
        if pyaudio:
            self.pya_client = pyaudio.PyAudio()
        else:
            LOGGER.warning("PyAudio not available; audio capture/playback will be disabled")

    async def open_mic(self) -> None:
        """
        Open the default microphone stream.

        Queries the default input device and opens an audio stream with
        the configured sample rate and chunk size.

        Raises:
            RuntimeError: If microphone initialization fails or PyAudio is missing
        """
        if not self.pya_client:
            raise RuntimeError("PyAudio is not installed or initialized")
            
        device_info = await asyncio.to_thread(self.pya_client.get_default_input_device_info)
        LOGGER.info(
            "Using input device: %s (index=%s)",
            device_info.get("name"),
            device_info.get("index"),
        )
        self.mic_stream = await asyncio.to_thread(
            self.pya_client.open,
            format=self.config.format,
            channels=self.config.channels,
            rate=self.config.send_sample_rate,
            input=True,
            input_device_index=int(device_info["index"]),
            frames_per_buffer=self.config.chunk_size,
        )
        LOGGER.info("Microphone stream opened")

    async def open_speaker(self) -> None:
        """
        Open the default speaker/output stream.

        Opens an audio stream with the configured playback sample rate.

        Raises:
            RuntimeError: If speaker initialization fails or PyAudio means is missing
        """
        if not self.pya_client:
            raise RuntimeError("PyAudio is not installed or initialized")

        self.speaker_stream = await asyncio.to_thread(
            self.pya_client.open,
            format=self.config.format,
            channels=self.config.channels,
            rate=self.config.receive_sample_rate,
            output=True,
        )
        LOGGER.info("Speaker stream opened")

    async def close(self) -> None:
        """
        Close all audio streams and terminate PyAudio.

        Safely closes any open streams and terminates PyAudio client.
        Non-blocking and logs any errors encountered.
        """
        for stream_name in ("mic_stream", "speaker_stream"):
            stream = getattr(self, stream_name)
            if stream:
                try:
                    await asyncio.to_thread(stream.close)
                    LOGGER.debug("Closed %s", stream_name)
                except Exception as exc:  # noqa: BLE001
                    LOGGER.warning("Failed to close %s: %s", stream_name, exc)
                    LOGGER.warning("Failed to close %s: %s", stream_name, exc)
        
        if self.pya_client:
            self.pya_client.terminate()
            LOGGER.info("PyAudio terminated")
