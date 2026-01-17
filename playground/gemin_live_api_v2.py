"""Production-ready Gemini Live API client for guided form completion.

This module streams microphone audio to Gemini Live, handles tool calls to
persist user data, and plays back synthesized speech. It is structured for
handover to production: clear configuration, logging, error handling, and
separation of concerns.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional

import pyaudio
from google import genai
from google.genai import types

# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------
LOG_LEVEL = os.getenv("APP_LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
LOGGER = logging.getLogger("gemini_live")

# ---------------------------------------------------------------------------
# Audio configuration
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class AudioConfig:
    format: int = pyaudio.paInt16
    channels: int = 1
    send_sample_rate: int = 16000
    receive_sample_rate: int = 24000
    chunk_size: int = 1024
    mic_queue_maxsize: int = 5


audio_cfg = AudioConfig()

# ---------------------------------------------------------------------------
# Tooling and model configuration
# ---------------------------------------------------------------------------
MODEL_NAME = "gemini-2.5-flash-native-audio-latest"
SYSTEM_PROMPT = (
    "You are a helpful assistant collecting Munich Meldeschein data.\n"
    "After each user interaction, call update_user_info with collected data.\n"
    "Ask for: name, date of move, street, postal code, city."
)


def _build_function_declarations() -> List[types.FunctionDeclaration]:
    """Return the list of tool/function declarations exposed to the model."""
    update_user_info = types.FunctionDeclaration(
        name="update_user_info",
        description=(
            "Updates the current user information being collected for the "
            "Meldeschein form."
        ),
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "name": types.Schema(
                    type=types.Type.STRING,
                    description="User's full name",
                ),
                "date_of_move": types.Schema(
                    type=types.Type.STRING,
                    description="Date of move (e.g., 2025-01-15)",
                ),
                "street": types.Schema(
                    type=types.Type.STRING,
                    description="Street address",
                ),
                "postal_code": types.Schema(
                    type=types.Type.STRING,
                    description="Postal code",
                ),
                "city": types.Schema(
                    type=types.Type.STRING,
                    description="City name",
                ),
                "previous_address": types.Schema(
                    type=types.Type.STRING,
                    description="Previous address",
                ),
            },
        ),
    )

    # Future extension: add get_next_form_field, validate_form_field,
    # save_form_field once their signatures are finalized.
    return [update_user_info]


def _build_tool_config() -> types.Tool:
    """Build the Tool configuration for the live session."""
    return types.Tool(function_declarations=_build_function_declarations())


def build_genai_config() -> Dict[str, Any]:
    """Create the GenAI Live API configuration payload."""
    return {
        "response_modalities": ["AUDIO"],
        "system_instruction": SYSTEM_PROMPT,
        "input_audio_transcription": {},
        "output_audio_transcription": {},
        "tools": [_build_tool_config()],
    }


# ---------------------------------------------------------------------------
# Domain data structures
# ---------------------------------------------------------------------------
@dataclass
class UserProfile:
    """Structured container for user information collected via tool calls."""

    name: Optional[str] = None
    date_of_move: Optional[str] = None
    street: Optional[str] = None
    postal_code: Optional[str] = None
    city: Optional[str] = None
    previous_address: Optional[str] = None

    def update_from_args(self, args: Dict[str, Any]) -> None:
        """Apply model-supplied arguments to the profile, skipping Nones."""
        for key, value in args.items():
            if value is not None and hasattr(self, key):
                setattr(self, key, value)
                LOGGER.debug("Updated user profile field %s=%s", key, value)

    def to_serializable(self) -> Dict[str, Any]:
        """Return a JSON-serializable representation of the profile."""
        return self.__dict__.copy()


@dataclass
class AudioPipelines:
    """Wraps PyAudio input/output streams and async queues."""

    config: AudioConfig
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


# ---------------------------------------------------------------------------
# Async pipeline tasks
# ---------------------------------------------------------------------------
async def listen_to_microphone(audio: AudioPipelines, stop_event: asyncio.Event) -> None:
    """Capture audio from microphone and enqueue for sending."""
    await audio.open_mic()
    kwargs = {"exception_on_overflow": False}
    try:
        while not stop_event.is_set():
            data = await asyncio.to_thread(audio.mic_stream.read, audio.config.chunk_size, **kwargs)  # type: ignore[arg-type]
            try:
                audio.mic_queue.put_nowait({"data": data, "mime_type": "audio/pcm"})
            except asyncio.QueueFull:
                LOGGER.debug("Microphone queue full; dropping audio chunk")
    except Exception as exc:  # noqa: BLE001
        LOGGER.error("Microphone read failed: %s", exc, exc_info=LOG_LEVEL == "DEBUG")
        stop_event.set()


async def send_realtime_audio(session: Any, audio: AudioPipelines, play_guard: asyncio.Event, stop_event: asyncio.Event) -> None:
    """Send microphone audio to Gemini Live, avoiding echo during playback."""
    send_count = 0
    while not stop_event.is_set():
        msg = await audio.mic_queue.get()
        if play_guard.is_set():
            LOGGER.debug("Dropping mic chunk while playback is active")
            continue
        try:
            await session.send_realtime_input(audio=msg)
            send_count += 1
            if send_count % 50 == 0:
                LOGGER.info("Sent %s audio chunks to Gemini", send_count)
        except Exception as exc:  # noqa: BLE001
            LOGGER.error("Failed to send audio chunk: %s", exc)
            stop_event.set()


async def play_audio(audio: AudioPipelines, play_guard: asyncio.Event, stop_event: asyncio.Event) -> None:
    """Play synthesized audio returned by the model."""
    await audio.open_speaker()
    try:
        while not stop_event.is_set():
            bytestream = await audio.playback_queue.get()
            play_guard.set()
            try:
                await asyncio.to_thread(audio.speaker_stream.write, bytestream)  # type: ignore[arg-type]
            except Exception as exc:  # noqa: BLE001
                LOGGER.error("Speaker write failed: %s", exc)
                stop_event.set()
            finally:
                if audio.playback_queue.empty():
                    play_guard.clear()
    except Exception as exc:  # noqa: BLE001
        LOGGER.error("Playback loop error: %s", exc)
        stop_event.set()


async def _handle_tool_calls(
    tool_call: types.ToolCall,
    session: Any,
    user_profile: UserProfile,
) -> None:
    """Process tool calls from the model and respond appropriately."""
    if not tool_call.function_calls:
        return

    function_responses: List[types.FunctionResponse] = []
    for func_call in tool_call.function_calls:
        LOGGER.info("Tool call received: %s", func_call.name)
        if func_call.name == "update_user_info":
            args = func_call.args or {}
            user_profile.update_from_args(args)
            LOGGER.info("User profile updated: %s", json.dumps(user_profile.to_serializable(), indent=2))
            function_responses.append(
                types.FunctionResponse(
                    id=func_call.id,
                    name=func_call.name,
                    response={"output": "User info stored"},
                )
            )
        else:
            LOGGER.warning("Unhandled tool call: %s", func_call.name)

    if function_responses:
        await session.send_tool_response(function_responses=function_responses)
        LOGGER.debug("Sent tool response to model")


async def receive_from_model(
    session: Any,
    audio: AudioPipelines,
    play_guard: asyncio.Event,
    stop_event: asyncio.Event,
    user_profile: UserProfile,
) -> None:
    """Receive streaming responses from the model and route to handlers."""
    response_count = 0
    while not stop_event.is_set():
        try:
            async for response in session.receive():
                response_count += 1
                LOGGER.debug("Received response #%s", response_count)

                if response.tool_call:
                    await _handle_tool_calls(response.tool_call, session, user_profile)

                if response.tool_call_cancellation:
                    LOGGER.warning("Tool call cancellation signaled by model")

                server_content = response.server_content
                if not server_content:
                    continue

                if server_content.interrupted:
                    LOGGER.info("Model interrupted current turn; clearing playback queue")
                    play_guard.clear()
                    while not audio.playback_queue.empty():
                        audio.playback_queue.get_nowait()

                if server_content.model_turn:
                    parts = server_content.model_turn.parts or []
                    LOGGER.info("Model turn with %s part(s)", len(parts))
                    for part in parts:
                        if part.thought:
                            LOGGER.debug("Model thought: %s", part.thought)
                        if part.text:
                            LOGGER.info("Model text: %s", part.text)
                        if part.inline_data and isinstance(part.inline_data.data, bytes):
                            LOGGER.debug("Received %s bytes of audio data", len(part.inline_data.data))
                            audio.playback_queue.put_nowait(part.inline_data.data)

                if server_content.input_transcription and server_content.input_transcription.text:
                    LOGGER.info("User said: %s", server_content.input_transcription.text)

                if server_content.output_transcription and server_content.output_transcription.text:
                    LOGGER.info("Model (voice): %s", server_content.output_transcription.text)

        except Exception as exc:  # noqa: BLE001
            LOGGER.error("Error while receiving model responses: %s", exc, exc_info=LOG_LEVEL == "DEBUG")
            stop_event.set()
            break


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------
async def run() -> None:
    """Main entry point to start the live audio workflow."""
    client = genai.Client()
    genai_config = build_genai_config()

    audio = AudioPipelines(config=audio_cfg)
    user_profile = UserProfile()
    stop_event = asyncio.Event()
    play_guard = asyncio.Event()  # True when we are playing audio (prevent echo)

    LOGGER.info("Connecting to Gemini model %s", MODEL_NAME)
    try:
        async with client.aio.live.connect(model=MODEL_NAME, config=genai_config) as session:
            LOGGER.info("Connected to Gemini Live; start speaking")
            try:
                async with asyncio.TaskGroup() as tg:
                    tg.create_task(listen_to_microphone(audio, stop_event))
                    tg.create_task(send_realtime_audio(session, audio, play_guard, stop_event))
                    tg.create_task(receive_from_model(session, audio, play_guard, stop_event, user_profile))
                    tg.create_task(play_audio(audio, play_guard, stop_event))
            except* Exception as exc_group:  # Python 3.11+ syntax for grouped errors
                LOGGER.error("Task group encountered errors: %s", exc_group)
                stop_event.set()
    except asyncio.CancelledError:
        LOGGER.info("Run loop cancelled")
    except Exception as exc:  # noqa: BLE001
        LOGGER.error("Fatal error in run loop: %s", exc, exc_info=LOG_LEVEL == "DEBUG")
    finally:
        await audio.close()
        LOGGER.info("Shutdown complete")


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        LOGGER.info("Interrupted by user")
