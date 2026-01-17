"""Validation helpers for form fields."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Callable, Dict, Tuple

from .schema import FormField

ValidationResult = Tuple[bool, str]


def _validate_non_empty(value: str) -> ValidationResult:
    if value and value.strip():
        return True, ""
    return False, "Please provide a value."


def _validate_date(value: str) -> ValidationResult:
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return True, ""
    except Exception:  # noqa: BLE001
        return False, "Use format YYYY-MM-DD."


def _validate_postal_code(value: str) -> ValidationResult:
    if re.fullmatch(r"\d{5}", value or ""):
        return True, ""
    return False, "Postal code must be 5 digits."


def _validate_text(value: str) -> ValidationResult:
    return _validate_non_empty(value)


FIELD_TYPE_VALIDATORS: Dict[str, Callable[[str], ValidationResult]] = {
    "date": _validate_date,
    "postal_code": _validate_postal_code,
    "text": _validate_text,
}


def validate_field(field: FormField, value: str) -> ValidationResult:
    """Validate a value for a given form field."""
    if field.required:
        ok, message = _validate_non_empty(value)
        if not ok:
            return ok, message

    validator = FIELD_TYPE_VALIDATORS.get(field.field_type)
    if validator:
        return validator(value or "")

    return True, ""
