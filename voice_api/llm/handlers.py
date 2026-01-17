"""
Tool response handlers for Gemini Live guided form workflow.

Processes tool calls from the model and sends back appropriate responses.
Handles:
- get_next_form_field: Return current field metadata or done signal
- validate_form_field: Validate input and return result
- save_form_field: Save value, advance state, return progress
- generate_anmeldung_pdf: Generate and save PDF, return result

This module is focused on response logic. Tool definitions are in tools.py.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any

from google.genai import types

from ..app.state import FormState
from ..app.validation import validate_field
from ..config import LOGGER
from ..core import generate_anmeldung_pdf

__all__ = ["handle_tool_calls"]


def _field_to_payload(field: Any) -> dict[str, Any]:
    """
    Convert a field to a serializable payload for tool responses.

    Args:
        field: The field to convert

    Returns:
        Dictionary with field metadata for JSON serialization
    """
    return {
        "field_id": field.field_id,
        "label": field.label,
        "description": field.description,
        "field_type": field.validator.type,
        "required": field.required,
        "examples": field.examples or [],
        "constraints": {},
    }


async def handle_tool_calls(
    tool_call: types.ToolCall, session: Any, form_state: FormState
) -> None:
    """
    Process tool calls from the model and send responses back.

    Routes to specific handlers for each tool and sends responses to the session.

    Args:
        tool_call: ToolCall object from model response
        session: Gemini Live session for sending responses
        form_state: Current form state to update/query
    """
    if not tool_call.function_calls:
        return

    responses: list[types.FunctionResponse] = []

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
            value = args.get("value", "")
            field = form_state.current_field()
            if not field:
                responses.append(
                    types.FunctionResponse(
                        id=func_call.id,
                        name=name,
                        response={
                            "is_valid": False,
                            "message": "No field to validate. Call get_next_form_field first.",
                        },
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
            value = args.get("value", "")
            field = form_state.current_field()
            if not field:
                responses.append(
                    types.FunctionResponse(
                        id=func_call.id,
                        name=name,
                        response={
                            "ok": False,
                            "message": "No field to save. Call get_next_form_field first.",
                        },
                    )
                )
            else:
                form_state.record_value(field.field_id, value)
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

        elif name == "generate_anmeldung_pdf":
            try:
                # Generate PDF from collected answers
                pdf_bytes = generate_anmeldung_pdf(form_state.answers)

                # Save to output folder with timestamp
                output_dir = "output"
                os.makedirs(output_dir, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"anmeldung_{timestamp}.pdf"
                output_path = os.path.join(output_dir, output_filename)

                with open(output_path, "wb") as f:
                    f.write(pdf_bytes)

                LOGGER.info("PDF generated and saved to %s", output_path)

                responses.append(
                    types.FunctionResponse(
                        id=func_call.id,
                        name=name,
                        response={
                            "ok": True,
                            "pdf_location": output_path,
                            "pdf_size_bytes": len(pdf_bytes),
                            "message": f"Anmeldung PDF successfully generated and saved to {output_path}",
                        },
                    )
                )
            except Exception as exc:  # noqa: BLE001
                LOGGER.error("PDF generation failed: %s", exc)
                responses.append(
                    types.FunctionResponse(
                        id=func_call.id,
                        name=name,
                        response={
                            "ok": False,
                            "error": str(exc),
                            "message": "Failed to generate PDF. Please check all required fields are filled.",
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
        log_payload = [
            {"id": r.id, "name": r.name, "response": r.response} for r in responses
        ]
        LOGGER.info("Tool responses: %s", json.dumps(log_payload))
        await session.send_tool_response(function_responses=responses)
        LOGGER.debug("Sent %s tool responses", len(responses))
