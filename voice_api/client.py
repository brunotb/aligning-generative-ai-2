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


def build_genai_config() -> dict:
    """Build the Live API configuration payload."""
    return {
        "response_modalities": ["AUDIO"],
        "system_instruction": build_system_prompt(),
        "input_audio_transcription": {},
        "output_audio_transcription": {},
        "tools": [build_tool_config()],
    }


async def listen_to_microphone(audio: AudioPipelines, stop_event: asyncio.Event) -> None:
    """Capture audio from microphone and enqueue for sending."""
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

    LOGGER.info("Connecting to model %s", MODEL_NAME)
    try:
        async with client.aio.live.connect(model=MODEL_NAME, config=config) as session:
            LOGGER.info("Connected to Gemini Live; start speaking")
            try:
                async with asyncio.TaskGroup() as tg:
                    tg.create_task(listen_to_microphone(audio, stop_event))
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
