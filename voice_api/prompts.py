"""Prompt helpers for the Gemini Live workflow."""

from __future__ import annotations

from .config import SYSTEM_PROMPT_BASE
from .schema import FORM_FIELDS


def build_system_prompt() -> str:
    """
    Generate the system prompt with complete field information.

    Builds a detailed system prompt that instructs the model to:
    1. Collect all form fields in order
    2. Validate each field appropriately
    3. Generate the PDF at the end

    Field descriptions are included from FORM_FIELDS, which are derived from
    the authoritative anmeldung_fields.py definitions.

    Returns:
        Complete system prompt string ready for Gemini Live API
    """
    field_lines = [f"- {f.label}: {f.description}" for f in FORM_FIELDS]
    fields_text = "\n".join(field_lines)

    return (
        SYSTEM_PROMPT_BASE
        + "\nAll required fields to collect:\n"
        + fields_text
        + "\n\nValidation rules:\n"
        + "- Dates must be in DD.MM.YYYY format\n"
        + "- Postal codes are 4-5 German digits\n"
        + "- Choice fields require the numeric index (e.g., 0, 1, 2)\n"
        + "- All fields are required for form completion\n"
        + "\nWhen all fields are collected and validated, call generate_anmeldung_pdf to create the final form."
    )
