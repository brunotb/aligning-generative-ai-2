"""Main runtime for Gemini Live guided form completion."""

from __future__ import annotations

import asyncio
from typing import Any

from google import genai

from .audio import AudioPipelines
from .config import LOGGER, MODEL_NAME
from .prompts import build_system_prompt
from .state import FormState
from .tools import build_tool_config, handle_tool_calls
from .vad import VoiceActivityDetector, VADConfig, SpeechState


def build_genai_config() -> dict:
    """Build the Live API configuration payload."""
    return {
        "response_modalities": ["AUDIO"],
        "system_instruction": build_system_prompt(),
        "input_audio_transcription": {},
        "output_audio_transcription": {},
        "tools": [build_tool_config()],
    }


async def listen_to_microphone(
    audio: AudioPipelines,
    vad: VoiceActivityDetector,
    stop_event: asyncio.Event,
) -> None:
    """Capture audio from microphone, apply VAD, and enqueue speech for sending."""
    await audio.open_mic()
    kwargs = {"exception_on_overflow": False}
    
    # Buffer to hold pre-speech context (last ~500ms before speech starts)
    pre_speech_buffer = []
    max_buffer_size = 17  # ~500ms at 30ms per frame
    is_currently_speaking = False
    post_speech_frames = 0  # Count frames after speech ends
    max_post_speech_frames = 10  # Send ~300ms of silence after speech
    
    try:
        while not stop_event.is_set():
            data = await asyncio.to_thread(
                audio.mic_stream.read, audio.config.chunk_size, **kwargs  # type: ignore[arg-type]
            )
            
            # Process through VAD
            state = vad.process_frame(data)
            
            # Handle state transitions
            if state == SpeechState.SPEAKING and not is_currently_speaking:
                # Speech just started - send buffered context first
                LOGGER.info("Speech started, flushing buffer (%d frames)", len(pre_speech_buffer))
                for buffered_data in pre_speech_buffer:
                    try:
                        audio.mic_queue.put_nowait({"data": buffered_data, "mime_type": "audio/pcm"})
                    except asyncio.QueueFull:
                        LOGGER.debug("Queue full while flushing buffer")
                pre_speech_buffer.clear()
                is_currently_speaking = True
                post_speech_frames = 0
            
            if state == SpeechState.SPEECH_ENDED and is_currently_speaking:
                LOGGER.info("Speech ended, sending trailing silence")
                is_currently_speaking = False
                post_speech_frames = 1  # Start counting post-speech frames
            
            # Send audio logic
            if is_currently_speaking or post_speech_frames > 0:
                # Active speech or post-speech silence - send immediately
                try:
                    audio.mic_queue.put_nowait({"data": data, "mime_type": "audio/pcm"})
                except asyncio.QueueFull:
                    LOGGER.debug("Microphone queue full; dropping audio chunk")
                
                # Track post-speech frames
                if post_speech_frames > 0:
                    post_speech_frames += 1
                    if post_speech_frames >= max_post_speech_frames:
                        LOGGER.info("Trailing silence sent, ready for model response")
                        post_speech_frames = 0
                        vad.reset()
            else:
                # Silence - buffer for context
                pre_speech_buffer.append(data)
                if len(pre_speech_buffer) > max_buffer_size:
                    pre_speech_buffer.pop(0)
                
    except Exception as exc:  # noqa: BLE001
        LOGGER.error("Microphone read failed: %s", exc)
        stop_event.set()


async def send_realtime_audio(
    session: Any,
    audio: AudioPipelines,
    play_guard: asyncio.Event,
    stop_event: asyncio.Event,
) -> None:
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
                LOGGER.info("Sent %s audio chunks", send_count)
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
    """Receive streaming responses from the model and route to handlers."""
    response_count = 0
    while not stop_event.is_set():
        try:
            async for response in session.receive():
                response_count += 1
                LOGGER.debug("Response #%s", response_count)

                if response.tool_call:
                    await handle_tool_calls(response.tool_call, session, form_state)

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
                    LOGGER.debug("Model turn with %s part(s)", len(parts))
                    for part in parts:
                        if part.thought:
                            LOGGER.debug("Model thought: %s", part.thought)
                        if part.text:
                            LOGGER.info("Model text: %s", part.text)
                        if part.inline_data and isinstance(part.inline_data.data, bytes):
                            audio.playback_queue.put_nowait(part.inline_data.data)

                if server_content.input_transcription and server_content.input_transcription.text:
                    LOGGER.info("User said: %s", server_content.input_transcription.text)

                if server_content.output_transcription and server_content.output_transcription.text:
                    LOGGER.info("Model (voice): %s", server_content.output_transcription.text)

        except Exception as exc:  # noqa: BLE001
            LOGGER.error("Error while receiving model responses: %s", exc)
            stop_event.set()
            break


async def run() -> None:
    """Run the live voice workflow."""
    client = genai.Client()
    config = build_genai_config()

    audio = AudioPipelines()
    form_state = FormState()
    stop_event = asyncio.Event()
    play_guard = asyncio.Event()
    
    # Initialize VAD with configuration optimized for 16kHz audio
    # More sensitive settings to catch speech quickly but filter background noise
    vad_config = VADConfig(
        sample_rate=16000,
        frame_duration_ms=30,
        aggressiveness=3,  # Most aggressive filtering to ignore background
        speech_start_frames=2,  # ~60ms to start (faster response)
        speech_end_frames=20,  # ~600ms of silence to end (longer pause)
        min_speech_duration=0.4,  # Ignore short bursts/background chatter
        max_speech_duration=30.0,  # Auto-cutoff for long speech
    )
    vad = VoiceActivityDetector(vad_config)
    LOGGER.info("VAD initialized")

    LOGGER.info("Connecting to model %s", MODEL_NAME)
    try:
        async with client.aio.live.connect(model=MODEL_NAME, config=config) as session:
            LOGGER.info("Connected to Gemini Live; start speaking")
            try:
                async with asyncio.TaskGroup() as tg:
                    tg.create_task(listen_to_microphone(audio, vad, stop_event))
                    tg.create_task(send_realtime_audio(session, audio, play_guard, stop_event))
                    tg.create_task(receive_from_model(session, audio, play_guard, stop_event, form_state))
                    tg.create_task(play_audio(audio, play_guard, stop_event))
            except* Exception as exc_group:  # Python 3.11+
                LOGGER.error("Task group encountered errors: %s", exc_group)
                stop_event.set()
    except asyncio.CancelledError:
        LOGGER.info("Run loop cancelled")
    except Exception as exc:  # noqa: BLE001
        LOGGER.error("Fatal error in run loop: %s", exc)
    finally:
        await audio.close()
        LOGGER.info("Shutdown complete")


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        LOGGER.info("Interrupted by user")
