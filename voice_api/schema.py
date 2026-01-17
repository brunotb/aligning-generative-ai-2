"""Form schema definitions for Anmeldung voice form.

This module provides FormField definitions by wrapping the authoritative field
definitions from anmeldung_fields.py. The actual field metadata (labels, descriptions,
validators, enums, examples) is defined in anmeldung_fields.py and should be updated
there.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Any

from .anmeldung_fields import ANMELDUNG_FORM_FIELDS, AnmeldungField


@dataclass(frozen=True)
class FormField:
    """
    Definition of a form field exposed to the model.

    This wraps AnmeldungField to provide a consistent interface to the rest of voice_api.
    All field metadata is derived from anmeldung_fields.py.

    Attributes:
        field_id: Unique voice-friendly field identifier
        label: Short human-readable label
        description: Detailed description from Anmeldung form
        field_type: Validator type (text, date_de, integer_choice, postal_code_de)
        required: Whether field is mandatory
        examples: Example valid inputs
        constraints: Additional constraints (for compatibility)
        pdf_field_id: Corresponding PDF field name
        validator_type: Type of validator (same as field_type)
        validator_config: Configuration dict for validator
        enum_values: Optional mapping of indices to display strings (for choice fields)
    """

    field_id: str
    label: str
    description: str
    field_type: str
    required: bool = True
    examples: Optional[List[str]] = None
    constraints: Optional[Dict[str, str]] = None
    pdf_field_id: Optional[str] = None
    validator_type: Optional[str] = None
    validator_config: Optional[Dict[str, Any]] = None
    enum_values: Optional[Dict[int, str]] = None


def _anmeldung_to_form_field(afield: AnmeldungField) -> FormField:
    """
    Convert an AnmeldungField to a FormField.

    Args:
        afield: AnmeldungField from anmeldung_fields.py

    Returns:
        FormField ready for use in voice_api
    """
    return FormField(
        field_id=afield.field_id,
        label=afield.label,
        description=afield.description,
        field_type=afield.validator.type,
        required=afield.required,
        examples=afield.examples,
        pdf_field_id=afield.pdf_field_id,
        validator_type=afield.validator.type,
        validator_config=afield.validator.config,
        enum_values=afield.enum_values,
    )


# Build the form fields from Anmeldung definitions
FORM_FIELDS: List[FormField] = [
    _anmeldung_to_form_field(f) for f in ANMELDUNG_FORM_FIELDS
]
"""
Complete list of form fields for the Anmeldung voice form.

Derived from anmeldung_fields.ANMELDUNG_FORM_FIELDS. Fields are presented
to the model in this order.
"""
