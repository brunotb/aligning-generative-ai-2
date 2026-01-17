# Voice API (Gemini Live) Guided Form Flow

This package provides a production-oriented Gemini Live client that guides users through completing a form using three tools:

- `get_next_form_field`: supplies the next field's metadata; signals completion when done.
- `validate_form_field`: validates a proposed value, returning `is_valid` and a message.
- `save_form_field`: persists a validated value and advances progress.

## Structure

- `config.py` – logging, model name, base prompt text, audio defaults.
- `audio.py` – microphone/speaker handling via `AudioPipelines`.
- `schema.py` – `FormField` dataclass and initial field catalog (expand to ~30 fields).
- `validation.py` – validators by field type and entry point `validate_field`.
- `state.py` – `FormState` tracking current field, answers, progress.
- `tools.py` – function declarations and tool-call handlers.
- `prompts.py` – system prompt builder that enumerates known fields.
- `client.py` – runtime orchestration (audio loops, tool routing, Gemini session).

## Running

```bash
python -m voice_api.client
```

Environment variables:

- `APP_LOG_LEVEL` (default `INFO`)
- `APP_MODEL_NAME` (default `gemini-2.5-flash-native-audio-latest`)

## Extending

- Add fields in `schema.py`; include constraints/examples to improve UX.
- Add or adjust validators in `validation.py` (regex/date/enum, etc.).
- If you need external validation/storage, swap implementations inside `tools.py` but keep response shapes stable.
- Update `SYSTEM_PROMPT_BASE` in `config.py` if the dialogue policy changes.

## Conversation loop contract

The model must follow: welcome → `get_next_form_field` → explain field → collect user reply → `validate_form_field` → if invalid, explain and retry; if valid, `save_form_field` → repeat → summarize when done.
