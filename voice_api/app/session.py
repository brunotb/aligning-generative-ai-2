"""
Gemini Live streaming session management.

Handles the core async tasks for voice communication:
- Microphone capture: Listen and enqueue microphone audio
- Audio sending: Send microphone data to model
- Model receive: Process model responses and route to handlers
- Audio playback: Play model-generated audio

Each task runs concurrently and uses async queues and events for coordination.
"""

from __future__ import annotations

import asyncio
from typing import Any

from ..app.audio import AudioPipelines
from ..app.state import FormState
from ..config import LOGGER

__all__ = [
    "listen_to_microphone",
    "send_realtime_audio",
    "receive_from_model",
    "play_audio",
]


async def listen_to_microphone(audio: AudioPipelines, stop_event: asyncio.Event) -> None:
    """
    Capture audio from microphone and enqueue for sending.

    Continuously reads from the microphone stream and puts audio chunks into
    the mic_queue for transmission to the model. Handles queue overflow gracefully.

    Args:
        audio: AudioPipelines instance with microphone stream
        stop_event: Event to signal loop termination

    Logs:
        - Queue full events (dropped chunks)
        - Microphone read failures (stops loop on error)
    """
    await audio.open_mic()
    kwargs = {"exception_on_overflow": False}
    try:
        while not stop_event.is_set():
            data = await asyncio.to_thread(
                audio.mic_stream.read, audio.config.chunk_size, **kwargs  # type: ignore[arg-type]
            )
            try:
                audio.mic_queue.put_nowait({"data": data, "mime_type": "audio/pcm"})
            except asyncio.QueueFull:
                LOGGER.debug("Microphone queue full; dropping audio chunk")
    except Exception as exc:  # noqa: BLE001
        LOGGER.error("Microphone read failed: %s", exc)
        stop_event.set()


async def send_realtime_audio(
    session: Any,
    audio: AudioPipelines,
    play_guard: asyncio.Event,
    stop_event: asyncio.Event,
) -> None:
    """
    Send microphone audio to Gemini Live, avoiding echo during playback.

    Dequeues microphone audio and sends to model. Uses play_guard to suppress
    transmission while model audio is playing (prevents echo).

    Args:
        session: Gemini Live session connection
        audio: AudioPipelines instance with mic_queue
        play_guard: Event indicating if speaker is actively playing
        stop_event: Event to signal loop termination

    Logs:
        - Suppressed chunks (during playback)
        - Send failures (stops loop on error)
        - Send count (every 50 chunks)
    """
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
                LOGGER.info("Sent %s audio chunks", send_count)
        except Exception as exc:  # noqa: BLE001
            LOGGER.error("Failed to send audio chunk: %s", exc)
            stop_event.set()


async def play_audio(
    audio: AudioPipelines, play_guard: asyncio.Event, stop_event: asyncio.Event
) -> None:
    """
    Play synthesized audio returned by the model.

    Dequeues audio from playback_queue and writes to speaker. Sets play_guard
    during playback to suppress microphone transmission (echo avoidance).

    Args:
        audio: AudioPipelines instance with speaker_stream and playback_queue
        play_guard: Event to signal when speaker is active
        stop_event: Event to signal loop termination

    Logs:
        - Playback errors (stops loop on error)
    """
    await audio.open_speaker()
    try:
        while not stop_event.is_set():
            bytestream = await audio.playback_queue.get()
            play_guard.set()
            try:
                await asyncio.to_thread(audio.speaker_stream.write, bytestream)  # type: ignore[arg-type]
            finally:
                if audio.playback_queue.empty():
                    play_guard.clear()
    except Exception as exc:  # noqa: BLE001
        LOGGER.error("Playback loop error: %s", exc)
        stop_event.set()


async def receive_from_model(
    session: Any,
    audio: AudioPipelines,
    play_guard: asyncio.Event,
    stop_event: asyncio.Event,
    form_state: FormState,
) -> None:
    """
    Receive streaming responses from the model and route to handlers.

    Processes incoming model messages:
    - Tool calls: Delegates to handle_tool_calls
    - Audio data: Enqueues for playback
    - Transcriptions: Logs user input and model output
    - Interrupts: Clears playback queue

    Args:
        session: Gemini Live session connection
        audio: AudioPipelines instance with playback_queue
        play_guard: Event indicating playback status (used for clearing on interrupt)
        stop_event: Event to signal loop termination
        form_state: Form state for tool calls (passed to handlers)

    Logs:
        - Response counts
        - Model thoughts and text
        - User transcription
        - Model voice output
        - Cancellations and interrupts
    """
    # Import here to avoid circular dependency between app and llm modules
    from ..llm import handle_tool_calls
    from ..api.events import FormEvent, event_emitter
    from ..api.voice_runner import voice_runner
    
    # Get current session ID
    session_id = voice_runner.get_current_session_id() or "default"
    
    response_count = 0
    while not stop_event.is_set():
        try:
            async for response in session.receive():
                response_count += 1
                LOGGER.debug("Response #%s", response_count)

                # Handle tool calls from model
                if response.tool_call:
                    await handle_tool_calls(response.tool_call, session, form_state)

                # Handle tool call cancellation
                if response.tool_call_cancellation:
                    LOGGER.warning("Tool call cancellation signaled by model")

                # Process server content
                server_content = response.server_content
                if not server_content:
                    continue

                # Handle interrupts (clear playback queue)
                if server_content.interrupted:
                    LOGGER.info("Model interrupted current turn; clearing playback queue")
                    play_guard.clear()
                    while not audio.playback_queue.empty():
                        audio.playback_queue.get_nowait()

                # Handle model turn (thoughts, text, and audio)
                if server_content.model_turn:
                    parts = server_content.model_turn.parts or []
                    LOGGER.debug("Model turn with %s part(s)", len(parts))
                    for part in parts:
                        if part.thought:
                            LOGGER.debug("Model thought: %s", part.thought)
                        if part.text:
                            LOGGER.info("Model text: %s", part.text)
                        if part.inline_data and isinstance(part.inline_data.data, bytes):
                            audio.playback_queue.put_nowait(part.inline_data.data)

                # Log input transcription (what user said)
                if (
                    server_content.input_transcription
                    and server_content.input_transcription.text
                ):
                    user_text = server_content.input_transcription.text
                    LOGGER.info("User said: %s", user_text)
                    
                    # Emit transcript event
                    event_emitter.emit_sync(
                        FormEvent(
                            type="transcript",
                            data={
                                "speaker": "user",
                                "text": user_text,
                            },
                            session_id=session_id,
                        )
                    )

                # Log output transcription (what model said)
                if (
                    server_content.output_transcription
                    and server_content.output_transcription.text
                ):
                    model_text = server_content.output_transcription.text
                    LOGGER.info("Model (voice): %s", model_text)
                    
                    # Emit transcript event
                    event_emitter.emit_sync(
                        FormEvent(
                            type="transcript",
                            data={
                                "speaker": "assistant",
                                "text": model_text,
                            },
                            session_id=session_id,
                        )
                    )

        except Exception as exc:  # noqa: BLE001
            LOGGER.error("Error while receiving model responses: %s", exc)
            stop_event.set()
            break
