"""
Field value validators for Anmeldung form.

This module provides validation for form field values according to German registration
form (Anmeldung) requirements. It supports:
- Text fields (non-empty)
- German date format (DDMMYYYY - 8 digits, no separators)
- German postal codes (4-5 digits)
- Integer choice fields (for radio buttons, dropdowns)

Validators are used both during form filling and PDF generation to ensure data integrity.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

ValidationResult = Tuple[bool, str]
"""Result of validation: (is_valid, error_message)."""


# ============================================================================
# INTERNAL VALIDATORS (one per type)
# ============================================================================


def _validate_non_empty(value: str) -> ValidationResult:
    """
    Check that a value is non-empty after stripping whitespace.

    Args:
        value: The value to validate

    Returns:
        (True, "") if valid, (False, error_msg) otherwise
    """
    if value and value.strip():
        return True, ""
    return False, "This field cannot be empty."


def _validate_text(value: str) -> ValidationResult:
    """
    Validate a text field (must be non-empty).

    Args:
        value: The text value to validate

    Returns:
        (True, "") if valid, (False, error_msg) otherwise
    """
    return _validate_non_empty(value)


def _validate_date_de(value: str) -> ValidationResult:
    """
    Validate German date format DDMMYYYY (8 digits, no separators).

    Takes full 4-digit year.
    Also validates that the date is actually valid (e.g., 3102 is rejected).

    Args:
        value: Date string to validate (8 digits: DDMMYYYY)

    Returns:
        (True, "") if valid, (False, error_msg) otherwise

    Examples:
        >>> _validate_date_de("15011990")
        (True, "")
        >>> _validate_date_de("15012025")
        (True, "")
        >>> _validate_date_de("32121990")
        (False, "Invalid date...")
    """
    if not value or not value.strip():
        return False, "Date cannot be empty."

    # Check format: exactly 8 digits (DDMMYYYY)
    pattern = r"^\d{8}$"
    if not re.match(pattern, value.strip()):
        return False, "Invalid format. Use DDMMYYYY (e.g., 15011990 for January 15, 1990)."

    try:
        value_str = value.strip()
        day = int(value_str[0:2])
        month = int(value_str[2:4])
        year = int(value_str[4:8])

        # Validate that the date is actually valid
        datetime(year, month, day)
        return True, ""
    except (ValueError, IndexError):
        return False, "Invalid date. Check day (1-31), month (1-12), year."


def _validate_integer_choice(
    value: str, min_val: int = 0, max_val: Optional[int] = None
) -> ValidationResult:
    """
    Validate an integer choice field (used for radio buttons, dropdowns).

    Args:
        value: The value to validate (should be an integer string)
        min_val: Minimum acceptable value (inclusive, default 0)
        max_val: Maximum acceptable value (inclusive, None for no max)

    Returns:
        (True, "") if valid, (False, error_msg) otherwise

    Examples:
        >>> _validate_integer_choice("0", 0, 3)
        (True, "")
        >>> _validate_integer_choice("5", 0, 3)
        (False, "Value 5 is too large...")
    """
    if not value or not value.strip():
        return False, "Value cannot be empty."

    try:
        num = int(value.strip())
    except ValueError:
        return False, "Must be a whole number (0, 1, 2, etc.)."

    if num < min_val:
        return False, f"Value {num} is too small (minimum {min_val})."

    if max_val is not None and num > max_val:
        return False, f"Value {num} is too large (maximum {max_val})."

    return True, ""


def _validate_postal_code_de(value: str) -> ValidationResult:
    """
    Validate German postal code (4 or 5 digits).

    Accepts both 4-digit (older) and 5-digit (standard) postal codes.

    Args:
        value: The postal code to validate

    Returns:
        (True, "") if valid, (False, error_msg) otherwise

    Examples:
        >>> _validate_postal_code_de("80802")
        (True, "")
        >>> _validate_postal_code_de("8080")
        (False, "Postal code must be 4 or 5 digits.")
    """
    if not value or not value.strip():
        return False, "Postal code cannot be empty."

    value_stripped = value.strip()

    # Accept both 4-digit (older) and 5-digit (standard) postal codes
    if re.fullmatch(r"\d{5}", value_stripped):
        return True, ""
    if re.fullmatch(r"\d{4}", value_stripped):
        return True, ""

    return False, "Postal code must be 4 or 5 digits."


# ============================================================================
# PUBLIC VALIDATION DISPATCHER
# ============================================================================


def validate_by_type(
    validator_type: str, value: str, config: Optional[Dict[str, Any]] = None
) -> ValidationResult:
    """
    Dispatch to the appropriate validator based on field type.

    This is the main entry point for validation. It routes to specific validators
    based on the field's validator_type and passes any configuration needed.

    Args:
        validator_type: Type of validator to use. Valid types:
            - "text": Non-empty text field
            - "date_de": German date format (DD.MM.YYYY or DD.MM.YY)
            - "postal_code_de": German postal code (4-5 digits)
            - "integer_choice": Integer within a range (for radio buttons, dropdowns)
        value: User input to validate
        config: Validator-specific configuration. Examples:
            - For "integer_choice": {"min": 0, "max": 3}
            - For "date_de": {"format": "DD.MM.YYYY"}
            - For "postal_code_de": No specific config used

    Returns:
        (True, "") if valid, (False, error_msg) otherwise

    Examples:
        >>> validate_by_type("text", "Mueller")
        (True, "")
        >>> validate_by_type("date_de", "15.01.1990")
        (True, "")
        >>> validate_by_type("integer_choice", "2", {"min": 0, "max": 3})
        (True, "")
        >>> validate_by_type("postal_code_de", "80802")
        (True, "")
    """
    config = config or {}

    if validator_type == "text":
        return _validate_text(value)

    elif validator_type == "date_de":
        return _validate_date_de(value)

    elif validator_type == "postal_code_de":
        return _validate_postal_code_de(value)

    elif validator_type == "integer_choice":
        min_val = config.get("min", 0)
        max_val = config.get("max")
        return _validate_integer_choice(value, min_val, max_val)

    else:
        # Unknown validator type; pass through as valid (graceful fallback)
        return True, ""
