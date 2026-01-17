"""
Field validation wrapper for app logic.

Provides a simple interface for the app/workflow modules to validate form fields.
Dispatches to core validators and provides additional helper functions for enum
display and user-facing messages.

This module acts as a bridge between the app logic and the core validation module,
keeping the core module independent and the app logic clean.
"""

from __future__ import annotations

from ..core import ValidationResult, validate_by_type
from ..core.fields import AnmeldungField

__all__ = ["validate_field", "get_enum_display", "ValidationResult"]


def validate_field(field: AnmeldungField, value: str) -> ValidationResult:
    """
    Validate a form field value.

    Dispatches to the appropriate validator based on field.validator.type.
    Checks required fields and passes configuration to validators.

    Args:
        field: AnmeldungField with validator type and config
        value: User-provided value to validate

    Returns:
        (True, "") if valid, (False, error_message) if invalid

    Examples:
        >>> from voice_api.core import ANMELDUNG_FORM_FIELDS
        >>> field = ANMELDUNG_FORM_FIELDS[0]  # family_name_p1
        >>> validate_field(field, "Mueller")
        (True, "")
        >>> validate_field(field, "")
        (False, "... is required")
    """
    # Check required fields
    if field.required and (not value or not value.strip()):
        return False, f"{field.label} is required."

    # Empty value on optional field is OK
    if not value or not value.strip():
        return True, ""

    # Dispatch to validator based on field type
    validator_type = field.validator.type
    validator_config = field.validator.config or {}

    return validate_by_type(validator_type, value, validator_config)


def get_enum_display(field: AnmeldungField, value: str) -> str:
    """
    Get human-readable display string for an enum/choice field.

    Converts an integer index (as string) to a human-readable label using the
    field's enum_values mapping. Used for logging and user feedback.

    Args:
        field: AnmeldungField with enum_values mapping
        value: Integer value as string (e.g., "0", "1")

    Returns:
        Human-readable display string, or the original value if not found

    Examples:
        >>> from voice_api.core import ANMELDUNG_FORM_FIELDS
        >>> gender_field = [f for f in ANMELDUNG_FORM_FIELDS if f.field_id == "gender_p1"][0]
        >>> get_enum_display(gender_field, "0")
        'M (Male / Männlich)'
        >>> get_enum_display(gender_field, "1")
        'W (Female / Weiblich)'
    """
    if not field.enum_values:
        return value

    try:
        idx = int(value)
        return field.enum_values.get(idx, value)
    except (ValueError, TypeError):
        return value
