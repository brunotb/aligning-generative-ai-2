"""
Tool declarations for Gemini Live guided form workflow.

Defines the tools exposed to the model for collecting and validating form data.
Tools provided:
- get_next_form_field: Fetch the next field metadata
- validate_form_field: Validate user input for current field
- save_form_field: Save validated value and advance
- generate_anmeldung_pdf: Generate final PDF document

This module is responsible for tool definitions only. Tool response handling
is in handlers.py.
"""

from __future__ import annotations

from typing import Any, Dict, List

from google.genai import types

from ..core import AnmeldungField

__all__ = ["build_function_declarations", "build_tool_config"]


def _field_to_payload(field: AnmeldungField) -> Dict[str, Any]:
    """
    Convert an AnmeldungField to a serializable payload for tool responses.

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


def build_function_declarations() -> List[types.FunctionDeclaration]:
    """
    Define all tool functions exposed to the model.

    Returns:
        List of FunctionDeclaration objects for the Gemini Live session
    """
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
                "You MUST provide the field_id of the current field to confirm you're validating the right field. "
                "Returns validation result."
            ),
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "field_id": types.Schema(
                        type=types.Type.STRING,
                        description="The field_id of the CURRENT field you are validating (MUST match the current field from get_next_form_field)",
                    ),
                    "value": types.Schema(
                        type=types.Type.STRING,
                        description="User-provided value to validate",
                    ),
                },
                required=["field_id", "value"],
            ),
        ),
        types.FunctionDeclaration(
            name="save_form_field",
            description=(
                "Save the validated value for the CURRENT field and advance to next. "
                "You MUST provide the field_id of the current field to confirm you're saving to the right field. "
                "Always call after validate_form_field returns is_valid=true."
            ),
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "field_id": types.Schema(
                        type=types.Type.STRING,
                        description="The field_id of the CURRENT field you are saving (MUST match the current field from get_next_form_field)",
                    ),
                    "value": types.Schema(
                        type=types.Type.STRING,
                        description="Validated value to save",
                    ),
                },
                required=["field_id", "value"],
            ),
        ),
        types.FunctionDeclaration(
            name="navigate_to_field",
            description=(
                "Navigate to a specific field by field_id. Use this when the user wants to "
                "correct or review a previously entered field. Returns the field metadata."
            ),
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "field_id": types.Schema(
                        type=types.Type.STRING,
                        description="The field_id to navigate to (e.g., 'first_name', 'birth_date')",
                    ),
                },
                required=["field_id"],
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
        types.FunctionDeclaration(
            name="get_all_answers",
            description=(
                "Return all completed field IDs, labels, and their values. "
                "Use this to show the user what they've entered so far or to find a field ID for correction. "
                "Returns list of saved fields with their current values."
            ),
            parameters=types.Schema(type=types.Type.OBJECT, properties={}),
        ),
        types.FunctionDeclaration(
            name="update_previous_field",
            description=(
                "Update the value of a PREVIOUSLY saved field. "
                "Can ONLY update fields that have already been completed (field index < current index). "
                "Cannot update the current field or skip ahead to future fields. "
                "Always validate the new value before calling this. "
                "Returns validation result and whether update was allowed."
            ),
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "field_id": types.Schema(
                        type=types.Type.STRING,
                        description="The field_id of the previously saved field to update (get from get_all_answers)",
                    ),
                    "value": types.Schema(
                        type=types.Type.STRING,
                        description="New validated value to save",
                    ),
                },
                required=["field_id", "value"],
            ),
        ),
    ]


def build_tool_config() -> types.Tool:
    """
    Construct the Tool configuration object for the live session.

    Returns:
        Tool object with all function declarations ready for Gemini Live
    """
    return types.Tool(function_declarations=build_function_declarations())
