"""
Main runtime for Gemini Live guided form completion.

This is the entry point for running the voice-guided Anmeldung form flow.
It orchestrates:
1. Audio pipeline (microphone and speaker)
2. Gemini Live session connection
3. Async task coordination (capture, send, receive, play)
4. Graceful shutdown

To run the application:
    python -m voice_api.client

Environment variables:
    APP_MODEL_NAME: Gemini model to use (default: gemini-2.5-flash-native-audio-preview-09-2025)
    APP_LOG_LEVEL: Logging level (default: INFO)
    GOOGLE_API_KEY: Google API key for Gemini API
"""

from __future__ import annotations

import asyncio

from google import genai

from .app import AudioPipelines, FormState, listen_to_microphone, play_audio, receive_from_model, send_realtime_audio
from .config import LOGGER, MODEL_NAME
from .llm import build_system_prompt, build_tool_config

__all__ = ["build_genai_config", "run"]


def build_genai_config() -> dict:
    """
    Build the Gemini Live API configuration payload.

    Configures:
    - Response modalities (audio output)
    - System instruction (from prompts module)
    - Audio transcription (for logging user/model speech)
    - Tool declarations (form interaction tools)

    Returns:
        Configuration dict for client.aio.live.connect()
    """
    return {
        "response_modalities": ["AUDIO"],
        "system_instruction": build_system_prompt(),
        "input_audio_transcription": {},
        "output_audio_transcription": {},
        "tools": [build_tool_config()],
    }


async def run() -> None:
    """
    Run the live voice workflow.

    Orchestrates the complete form filling experience:
    1. Connects to Gemini Live API
    2. Spawns concurrent tasks for audio capture, sending, receiving, and playback
    3. Manages task lifecycle and error handling
    4. Cleans up audio resources on shutdown

    Logs:
        - Connection status
        - Task errors
        - Graceful shutdown signals

    Raises:
        KeyboardInterrupt: User interrupted (handled gracefully)
        Exception: Fatal errors in the run loop (logged)
    """
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
                    # Start all concurrent tasks
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
