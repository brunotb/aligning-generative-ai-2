"""Tool declarations and handlers for the guided form flow."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from google.genai import types

from .config import LOGGER
from .schema import FormField
from .state import FormState
from .validation import validate_field


def _field_to_payload(field: FormField) -> Dict[str, Any]:
    """Convert a FormField to a serializable payload for tool responses."""
    return {
        "field_id": field.field_id,
        "label": field.label,
        "description": field.description,
        "field_type": field.field_type,
        "required": field.required,
        "examples": field.examples or [],
        "constraints": field.constraints or {},
    }


def build_function_declarations() -> List[types.FunctionDeclaration]:
    """Define all tool functions exposed to the model."""
    return [
        types.FunctionDeclaration(
            name="get_next_form_field",
            description=(
                "Return metadata for the next form field to fill. Returns done=true when finished."
            ),
            parameters=types.Schema(type=types.Type.OBJECT, properties={}),
        ),
        types.FunctionDeclaration(
            name="validate_form_field",
            description="Validate a value for a specific field and return a message if invalid.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "field_id": types.Schema(type=types.Type.STRING, description="ID of the field"),
                    "value": types.Schema(type=types.Type.STRING, description="User-provided value"),
                },
                required=["field_id", "value"],
            ),
        ),
        types.FunctionDeclaration(
            name="save_form_field",
            description="Persist a validated value for the given field and advance progress.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "field_id": types.Schema(type=types.Type.STRING, description="ID of the field"),
                    "value": types.Schema(type=types.Type.STRING, description="Validated value"),
                },
                required=["field_id", "value"],
            ),
        ),
    ]


def build_tool_config() -> types.Tool:
    """Construct the Tool configuration object for the live session."""
    return types.Tool(function_declarations=build_function_declarations())


async def handle_tool_calls(tool_call: types.ToolCall, session: Any, form_state: FormState) -> None:
    """Process tool calls from the model and send responses back."""
    if not tool_call.function_calls:
        return

    responses: List[types.FunctionResponse] = []

    for func_call in tool_call.function_calls:
        name = func_call.name
        args = func_call.args or {}
        LOGGER.info("Tool call: %s args=%s", name, json.dumps(args))

        if name == "get_next_form_field":
            field = form_state.current_field()
            if not field:
                responses.append(
                    types.FunctionResponse(
                        id=func_call.id,
                        name=name,
                        response={"done": True},
                    )
                )
            else:
                responses.append(
                    types.FunctionResponse(
                        id=func_call.id,
                        name=name,
                        response={"done": False, "field": _field_to_payload(field)},
                    )
                )

        elif name == "validate_form_field":
            field_id = args.get("field_id")
            value = args.get("value", "")
            field = _find_field(form_state, field_id)
            if not field:
                responses.append(
                    types.FunctionResponse(
                        id=func_call.id,
                        name=name,
                        response={"is_valid": False, "message": "Unknown field."},
                    )
                )
            else:
                is_valid, message = validate_field(field, value)
                if not is_valid:
                    form_state.set_error(field.field_id, message)
                responses.append(
                    types.FunctionResponse(
                        id=func_call.id,
                        name=name,
                        response={"is_valid": is_valid, "message": message},
                    )
                )

        elif name == "save_form_field":
            field_id = args.get("field_id")
            value = args.get("value", "")
            field = _find_field(form_state, field_id)
            if not field:
                responses.append(
                    types.FunctionResponse(
                        id=func_call.id,
                        name=name,
                        response={"ok": False, "message": "Unknown field."},
                    )
                )
            else:
                form_state.record_value(field_id, value)
                form_state.advance()
                responses.append(
                    types.FunctionResponse(
                        id=func_call.id,
                        name=name,
                        response={
                            "ok": True,
                            "progress_percent": form_state.progress_percent(),
                        },
                    )
                )
        else:
            responses.append(
                types.FunctionResponse(
                    id=func_call.id,
                    name=name,
                    response={"error": f"Unhandled tool {name}"},
                )
            )

    if responses:
        await session.send_tool_response(function_responses=responses)
        LOGGER.debug("Sent %s tool responses", len(responses))


def _find_field(form_state: FormState, field_id: Optional[str]) -> Optional[FormField]:
    if not field_id:
        return None
    for field in form_state.fields:
        if field.field_id == field_id:
            return field
    return None
