"""Prompt helpers for the Gemini Live workflow."""

from __future__ import annotations

from .config import SYSTEM_PROMPT_BASE
from .schema import FORM_FIELDS


def build_system_prompt() -> str:
    """
    Generate the system prompt with complete field information.

    Builds a detailed system prompt that instructs the model to:
    1. Always use the exact workflow: get_next_form_field → validate → save → repeat
    2. Collect all form fields in order
    3. Validate each field appropriately
    4. Generate the PDF at the end

    Field descriptions are included from FORM_FIELDS, which are derived from
    the authoritative anmeldung_fields.py definitions.

    Returns:
        Complete system prompt string ready for Gemini Live API
    """
    field_lines = [f"- {f.label}: {f.description}" for f in FORM_FIELDS]
    fields_text = "\n".join(field_lines)

    return (
        SYSTEM_PROMPT_BASE
        + "\n=== MANDATORY WORKFLOW ===\n"
        + "You MUST follow this exact sequence for every field:\n"
        + "1. Call get_next_form_field() to retrieve the CURRENT field and its details\n"
        + "2. Extract the value from user input\n"
        + "3. Call validate_form_field(value) with the CURRENT field's value\n"
        + "4. If valid, call save_form_field(value) to save and advance\n"
        + "5. If invalid, explain the error and ask user to correct\n"
        + "6. Repeat for next field\n"
        + "\nIMPORTANT: validate_form_field and save_form_field operate on the CURRENT field.\n"
        + "Do NOT pass field_id - it will be inferred from get_next_form_field.\n"
        + "\nAll required fields to collect:\n"
        + fields_text
        + "\n\nValidation rules:\n"
        + "- Dates must be in DD.MM.YYYY format\n"
        + "- Postal codes are 4-5 German digits\n"
        + "- Choice fields require the numeric index (e.g., 0, 1, 2)\n"
        + "- All fields are required for form completion\n"
        + "\nWhen all fields are collected and validated, call generate_anmeldung_pdf to create the final form."
    )
