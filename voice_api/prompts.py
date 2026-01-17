"""Prompt helpers for the Gemini Live workflow."""

from __future__ import annotations

from .config import SYSTEM_PROMPT_BASE
from .schema import FORM_FIELDS


def build_system_prompt() -> str:
    """Generate the system prompt with field overview."""
    field_lines = [f"- {f.label}: {f.description}" for f in FORM_FIELDS]
    fields_text = "\n".join(field_lines)
    return (
        SYSTEM_PROMPT_BASE
        + "\nKnown fields to collect (do not skip):\n"
        + fields_text
        + "\nWhen done, summarize collected answers briefly."
    )
