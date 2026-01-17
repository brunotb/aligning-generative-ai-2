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
            description=(
                "Validate a value for the CURRENT field (from get_next_form_field). "
                "Returns validation result."
            ),
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "value": types.Schema(type=types.Type.STRING, description="User-provided value to validate"),
                },
                required=["value"],
            ),
        ),
        types.FunctionDeclaration(
            name="save_form_field",
            description=(
                "Save the validated value for the CURRENT field and advance to next. "
                "Always call after validate_form_field returns is_valid=true."
            ),
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "value": types.Schema(type=types.Type.STRING, description="Validated value to save"),
                },
                required=["value"],
            ),
        ),
        types.FunctionDeclaration(
            name="generate_anmeldung_pdf",
            description=(
                "Generate the filled Anmeldung PDF from all collected form data. "
                "Call this after all fields are successfully collected and validated."
            ),
            parameters=types.Schema(type=types.Type.OBJECT, properties={}),
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
                import os
                from datetime import datetime
                from .pdf_generator import generate_anmeldung_pdf

                # Generate PDF
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


def _find_field(form_state: FormState, field_id: Optional[str]) -> Optional[FormField]:
    if not field_id:
        return None
    for field in form_state.fields:
        if field.field_id == field_id:
            return field
    return None
