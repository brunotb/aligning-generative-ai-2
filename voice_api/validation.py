"""Validation helpers for form fields.

This module provides field validation by dispatching to validators in pdf_validators.py
based on the field's validator_type. It also provides helper functions for displaying
enum values to users.
"""

from __future__ import annotations

from typing import Tuple

from .schema import FormField
from .pdf_validators import validate_by_type

ValidationResult = Tuple[bool, str]
"""Result of validation: (is_valid, error_message)."""


def validate_field(field: FormField, value: str) -> ValidationResult:
    """
    Validate a form field value.

    Dispatches to the appropriate validator based on field.validator_type.
    Checks required fields and passes configuration to validators.

    Args:
        field: FormField with validator_type and validator_config
        value: User-provided value to validate

    Returns:
        (True, "") if valid, (False, error_message) if invalid

    Examples:
        >>> from voice_api.schema import FORM_FIELDS
        >>> field = FORM_FIELDS[0]  # family_name_p1
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
    validator_type = field.validator_type or "text"
    validator_config = field.validator_config or {}

    return validate_by_type(validator_type, value, validator_config)


def get_enum_display(field: FormField, value: str) -> str:
    """
    Get human-readable display string for an enum/choice field.

    Converts an integer index (as string) to a human-readable label using the
    field's enum_values mapping. Used for logging and user feedback.

    Args:
        field: FormField with enum_values mapping
        value: Integer value as string (e.g., "0", "1")

    Returns:
        Human-readable display string, or the original value if not found

    Examples:
        >>> from voice_api.schema import FORM_FIELDS
        >>> gender_field = [f for f in FORM_FIELDS if f.field_id == "gender_p1"][0]
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
