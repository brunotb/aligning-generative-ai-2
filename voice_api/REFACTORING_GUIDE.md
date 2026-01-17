"""Voice API Module Architecture and Developer Guide."""

# Voice API - Production-Ready Refactoring

## Overview

The `voice_api` package is a production-ready solution for collecting form data through voice interaction with Google's Gemini Live API. The application is designed for:

- **Munich Residence Registration (Anmeldung)** form filling via voice
- **German form validation** (dates, postal codes, text fields, choice fields)
- **PDF generation** from collected form data
- **LLM-guided workflow** with field-by-field collection

## Architecture

### Layer Structure

The codebase is organized into four independent layers, each with a specific responsibility:

```
┌─────────────────────────────────────────────────────────────┐
│ client.py - Main Entry Point (orchestrator)                │
└───────────────┬───────────────────────────────────────────────┘
                │
        ┌───────┴────────┐
        │                │
┌───────▼─────────────────┐  ┌────────────────────────────────┐
│ app/ - Runtime Layer    │  │ llm/ - LLM Integration Layer  │
│ • State management      │  │ • Prompts (system instruction)│
│ • Audio I/O             │  │ • Tool definitions            │
│ • Session orchestration │  │ • Response handlers           │
│ • Validation wrapper    │  └────────────────────────────────┘
└───────┬────────────────┘
        │
┌───────▼────────────────────────────────────────────────────┐
│ core/ - Validation & PDF Layer (independent)              │
│ • Field definitions (source of truth)                      │
│ • Field validators (text, date, postal, choice)           │
│ • PDF generation and transformation                        │
└────────────────────────────────────────────────────────────┘
        │
┌───────▼────────────────────────────────────────────────────┐
│ config.py - Configuration Layer                            │
│ • Logging setup                                             │
│ • Model selection                                           │
│ • Audio parameters                                          │
└────────────────────────────────────────────────────────────┘
```

### Module Responsibilities

#### 1. **core/** - Field Definitions and Validation (Independent)

The core layer is self-contained and can be used independently for form validation and PDF generation without requiring the LLM or app modules.

**Files:**
- `fields.py`: Field definitions (AnmeldungField), validator types, and lookup maps
- `validators.py`: Validation logic for each field type
- `pdf_generator.py`: PDF transformation and generation
- `__init__.py`: Public API exports

**Key Concepts:**
- **Single Source of Truth**: `core/fields.py` defines all form fields once
- **Lookup Maps**: `FIELD_BY_ID` and `FIELD_BY_PDF_ID` for efficient access
- **Type Safety**: AnmeldungField dataclass with FieldValidator configuration

**Example Usage:**
```python
from voice_api.core import ANMELDUNG_FORM_FIELDS, validate_by_type, generate_anmeldung_pdf

# Get field definitions
fields = ANMELDUNG_FORM_FIELDS
first_field = fields[0]

# Validate a value
is_valid, message = validate_by_type("text", "Mueller", {})

# Generate PDF
pdf_bytes = generate_anmeldung_pdf({"family_name_p1": "Mueller", ...})
```

#### 2. **llm/** - Gemini Live Integration

The LLM layer manages prompts, tool declarations, and response handling for Gemini Live.

**Files:**
- `prompts.py`: System prompts and workflow instructions
- `tools.py`: Tool/function declarations (what the model can call)
- `handlers.py`: Tool response processing and state updates
- `__init__.py`: Public API exports

**Key Concepts:**
- **Single Prompt Source**: All system instructions in `prompts.py`
- **Dynamic Prompts**: Prompts auto-include field descriptions from core/fields.py
- **Tool Separation**: Declarations in `tools.py`, handlers in `handlers.py`
- **Async Handlers**: All tool handlers are async-safe

**Example Usage:**
```python
from voice_api.llm import build_system_prompt, build_tool_config, handle_tool_calls

# Get full system prompt with field descriptions
prompt = build_system_prompt()

# Build tool config for Gemini Live
tool_config = build_tool_config()

# Handle tool calls from model (async)
await handle_tool_calls(tool_call, session, form_state)
```

#### 3. **app/** - Runtime and Orchestration

The app layer brings together core and LLM modules to create a complete workflow.

**Files:**
- `state.py`: FormState dataclass for tracking form progress
- `audio.py`: AudioPipelines for microphone/speaker I/O
- `session.py`: Async tasks for streaming (capture, send, receive, play)
- `validation.py`: Validation wrapper (bridges core validators to app logic)
- `__init__.py`: Public API exports

**Key Concepts:**
- **Stateful Flow**: FormState tracks current field, answers, and errors
- **Concurrent Async Tasks**: Separate tasks for I/O bound operations
- **Event Coordination**: Async events coordinate between tasks (stop_event, play_guard)
- **Queue-Based Decoupling**: AsyncQueues decouple producers (mic) from consumers (model)

**Example Usage:**
```python
from voice_api.app import FormState, AudioPipelines, validate_field

# Track form progress
form_state = FormState()
current_field = form_state.current_field()

# Validate current field
is_valid, message = validate_field(current_field, user_input)
if is_valid:
    form_state.record_value(current_field.field_id, user_input)
    form_state.advance()

# Audio pipeline
audio = AudioPipelines()
await audio.open_mic()
await audio.open_speaker()
await audio.close()
```

#### 4. **client.py** - Main Entry Point

The client module orchestrates the complete workflow.

**Example Usage:**
```python
from voice_api.client import run
import asyncio

asyncio.run(run())
```

Or via command line:
```bash
python -m voice_api.client
```

#### 5. **config.py** - Configuration

Central configuration for logging, model selection, and audio settings.

**Environment Variables:**
- `APP_LOG_LEVEL`: Logging level (default: INFO)
- `APP_MODEL_NAME`: Gemini model to use
- `GOOGLE_API_KEY`: Google API key

## Key Design Decisions

### 1. **Single Source of Truth for Fields**
- All field definitions are in `core/fields.py`
- Other modules reference this, never duplicate field data
- System prompts auto-generate from field definitions

### 2. **Core Layer Independence**
- `core/` has zero dependencies on `llm/` or `app/`
- Can be used standalone for CLI validators or batch PDF generation
- No async/await in core (simple, testable, reusable)

### 3. **Separation of Concerns**
- **core**: Data and validation logic
- **llm**: Model integration (Gemini Live specific)
- **app**: Runtime orchestration (async, stateful)
- **config**: Configuration and setup

### 4. **Clear Public APIs**
- Each module's `__init__.py` exports its public API
- Private functions start with `_` (e.g., `_validate_text`)
- Comprehensive docstrings explain usage

### 5. **Async/Await Discipline**
- Only `app/` and `client.py` use async/await
- `core/` is synchronous (easier to test, compose)
- `llm/handlers.py` is async to handle model responses

## Development Guidelines

### Adding a New Form Field

1. Add to `core/fields.py`:
   ```python
   NEW_FIELD = AnmeldungField(
       field_id="new_field_id",
       pdf_field_id="pdf_field_id",
       label="Field Label",
       description="Description",
       validator=FieldValidator(type="text"),
       examples=["example1"],
   )
   ```

2. Add to `ANMELDUNG_FORM_FIELDS` list in `core/fields.py`

3. System prompt and validation automatically pick it up

### Adding a New Validator Type

1. Create validator function in `core/validators.py`:
   ```python
   def _validate_new_type(value: str) -> ValidationResult:
       """Validate new type."""
       # implementation
       return True, ""
   ```

2. Add case to `validate_by_type()` dispatcher

3. Use in field definition:
   ```python
   validator=FieldValidator(type="new_type", config={...})
   ```

### Modifying System Prompt

- Edit `llm/prompts.py`
- Update `SYSTEM_PROMPT_BASE` for base instruction
- Update `build_system_prompt()` for additional sections
- Field descriptions auto-generate from core/fields.py

### Adding a New Tool

1. Add declaration to `llm/tools.py`:
   ```python
   types.FunctionDeclaration(
       name="new_tool",
       description="...",
       parameters=types.Schema(...),
   )
   ```

2. Add handler to `llm/handlers.py`:
   ```python
   elif name == "new_tool":
       # implementation
   ```

## File Size and Complexity Targets

All modules follow these guidelines:

- **Files**: 200-300 lines (target)
- **Functions**: 30-50 lines (target)
- **Classes**: Focused on single responsibility
- **Docstrings**: Google-style, comprehensive
- **Comments**: Explain "why", not "what"

## Testing Structure

Tests mirror the module structure:

- `tests/unit/test_*.py`: Unit tests for individual modules
- `tests/integration/test_*.py`: Integration tests
- All tests are independent (no shared state)
- Tests import from public APIs (`from voice_api.core import ...`)

## Error Handling

Each layer has appropriate error handling:

- **core**: Validation functions return (is_valid, message) tuples
- **llm**: Handlers catch exceptions and return error responses
- **app**: Async tasks catch exceptions and set stop_event
- **client**: Top-level try/except for graceful shutdown

## Performance Considerations

- **Audio Queue**: Limited size (5) to prevent memory buildup
- **Lazy Imports**: PyAudio imported only when needed
- **Lookup Maps**: Fast field access via FIELD_BY_ID
- **Async Tasks**: Concurrent I/O operations (no blocking)

## Production Deployment

### Prerequisites
- Python 3.10+
- `pip install -r requirements.txt`
- Google API key in `GOOGLE_API_KEY` environment variable

### Running
```bash
python -m voice_api.client
```

### Logs
- Set `APP_LOG_LEVEL=DEBUG` for verbose output
- All major operations are logged
- Audio queue issues logged at DEBUG level

## Troubleshooting

### "No field to validate" Error
- Ensure `get_next_form_field()` called before `validate_form_field()`
- Model is not following the mandatory workflow

### PDF Generation Fails
- Check PDF template exists at `documents/Anmeldung_Meldeschein_20220622.pdf`
- Verify all required fields are filled
- Check PyPDFForm is installed: `pip install PyPDFForm`

### Audio Issues
- Verify microphone is detected: `python -c "import pyaudio; p=pyaudio.PyAudio(); print(p.get_default_input_device_info())"`
- Check sample rates (16000 for input, 24000 for output)

## Migration Guide (from old structure)

### Old Structure → New Structure

| Old                    | New                                |
|------------------------|----------------------------------|
| `anmeldung_fields.py`  | `core/fields.py` (unchanged)     |
| `pdf_validators.py`    | `core/validators.py`             |
| `pdf_generator.py`     | `core/pdf_generator.py`          |
| `validation.py`        | `app/validation.py` (wrapper)    |
| `state.py`             | `app/state.py`                   |
| `audio.py`             | `app/audio.py`                   |
| `prompts.py`           | `llm/prompts.py`                 |
| `tools.py`             | `llm/tools.py` + `llm/handlers.py` |
| `client.py`            | `client.py` + `app/session.py`    |
| `schema.py`            | Removed (use `core/fields.py`)    |
| `config.py`            | `config.py` (updated)            |

### Import Changes

Old:
```python
from voice_api.anmeldung_fields import ANMELDUNG_FORM_FIELDS
from voice_api.validation import validate_field
```

New:
```python
from voice_api.core import ANMELDUNG_FORM_FIELDS
from voice_api.app import validate_field
```

## Future Improvements

- [ ] Configuration file support (YAML/JSON)
- [ ] Multiple language support (system prompts)
- [ ] Field-level customization (display format, validation rules)
- [ ] Metrics/analytics integration
- [ ] Mock LLM for testing
- [ ] Streaming PDF updates
