# Voice API (Gemini Live) Guided Form Flow

This package provides a production-oriented Gemini Live client that guides users through completing a form using three tools:

- `get_next_form_field`: supplies the next field's metadata; signals completion when done.
- `validate_form_field`: validates a proposed value, returning `is_valid` and a message.
- `save_form_field`: persists a validated value and advances progress.

## Structure

- `config.py` – logging, model name, base prompt text, audio defaults.
- `audio.py` – microphone/speaker handling via `AudioPipelines`.
- `vad.py` – Voice Activity Detection using WebRTC VAD (filters background noise).
- `schema.py` – `FormField` dataclass and initial field catalog (expand to ~30 fields).
- `validation.py` – validators by field type and entry point `validate_field`.
- `state.py` – `FormState` tracking current field, answers, progress.
- `tools.py` – function declarations and tool-call handlers.
- `prompts.py` – system prompt builder that enumerates known fields.
- `client.py` – runtime orchestration (audio loops, tool routing, Gemini session).

## Installation

Install required dependencies:

```bash
pip install google-genai pyaudio webrtcvad
```

**Note on `webrtcvad`**: This is the recommended VAD library used by Google, Zoom, and other production systems. If installation fails on your platform, the system will fall back to simple energy-based detection (less accurate but functional).

## Running

```bash
python -m voice_api.client
```

Environment variables:

- `APP_LOG_LEVEL` (default `INFO`)
- `APP_MODEL_NAME` (default `gemini-2.5-flash-native-audio-preview-09-2025`)

## Voice Activity Detection (VAD)

The system uses WebRTC VAD to intelligently detect when you're speaking and filter out background noise:

- **Automatic speech detection**: Only sends audio when you're actually speaking
- **Background noise filtering**: Ignores ambient noise, keyboard clicks, etc.
- **Smart end-of-speech detection**: Automatically stops recording after 450ms of silence
- **Configurable sensitivity**: Adjust via `VADConfig` in `client.py`

### VAD Configuration Options

You can tune VAD behavior in `client.py`:

- `aggressiveness` (0-3): Higher = more aggressive noise filtering (default: 2)
- `speech_start_frames`: Consecutive speech frames needed to start (default: 3)
- `speech_end_frames`: Consecutive silence frames needed to end (default: 15)
- `min_speech_duration`: Minimum speech length in seconds (default: 0.3s)
- `max_speech_duration`: Maximum speech length before auto-cutoff (default: 30s)

## Extending

- Add fields in `schema.py`; include constraints/examples to improve UX.
- Add or adjust validators in `validation.py` (regex/date/enum, etc.).
- If you need external validation/storage, swap implementations inside `tools.py` but keep response shapes stable.
- Update `SYSTEM_PROMPT_BASE` in `config.py` if the dialogue policy changes.
- Adjust VAD settings in `client.py` if needed for your environment (noisy vs. quiet).

## Conversation loop contract

The model must follow: welcome → `get_next_form_field` → explain field → collect user reply → `validate_form_field` → if invalid, explain and retry; if valid, `save_form_field` → repeat → summarize when done.
