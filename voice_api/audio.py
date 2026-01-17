"""Audio pipeline helpers for microphone capture and playback."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Optional

import pyaudio

from .config import AudioConfig, default_audio_config, LOGGER


@dataclass
class AudioPipelines:
    """Wrap PyAudio input/output streams and async queues."""

    config: AudioConfig = field(default_factory=default_audio_config)
    pya_client: pyaudio.PyAudio = field(default_factory=pyaudio.PyAudio)
    mic_stream: Optional[pyaudio.Stream] = None
    speaker_stream: Optional[pyaudio.Stream] = None
    mic_queue: asyncio.Queue = field(init=False)
    playback_queue: asyncio.Queue = field(init=False)

    def __post_init__(self) -> None:
        self.mic_queue = asyncio.Queue(maxsize=self.config.mic_queue_maxsize)
        self.playback_queue = asyncio.Queue()

    async def open_mic(self) -> None:
        """Open the default microphone stream."""
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
        """Open the speaker/output stream."""
        self.speaker_stream = await asyncio.to_thread(
            self.pya_client.open,
            format=self.config.format,
            channels=self.config.channels,
            rate=self.config.receive_sample_rate,
            output=True,
        )
        LOGGER.info("Speaker stream opened")

    async def close(self) -> None:
        """Close any open audio streams and terminate PyAudio."""
        for stream_name in ("mic_stream", "speaker_stream"):
            stream = getattr(self, stream_name)
            if stream:
                try:
                    await asyncio.to_thread(stream.close)
                    LOGGER.debug("Closed %s", stream_name)
                except Exception as exc:  # noqa: BLE001
                    LOGGER.warning("Failed to close %s: %s", stream_name, exc)
        self.pya_client.terminate()
        LOGGER.info("PyAudio terminated")
