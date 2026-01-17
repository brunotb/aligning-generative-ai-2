"""
Core module: Field definitions, validation, and PDF generation.

This module contains the fundamental building blocks for form processing:
- Field definitions (field types, validators, metadata)
- Validation logic (text, dates, postal codes, choices)
- PDF generation (transform and fill PDF documents)

The core module is independent and can be used standalone for form validation
and PDF generation without requiring the LLM or app modules.
"""

from .fields import (
    ANMELDUNG_FORM_FIELDS,
    AnmeldungField,
    FIELD_BY_ID,
    FIELD_BY_PDF_ID,
    FieldValidator,
)
from .pdf_generator import generate_anmeldung_pdf, transform_answers_to_pdf_format
from .validators import ValidationResult, validate_by_type

__all__ = [
    # Fields
    "ANMELDUNG_FORM_FIELDS",
    "AnmeldungField",
    "FieldValidator",
    "FIELD_BY_ID",
    "FIELD_BY_PDF_ID",
    # Validators
    "validate_by_type",
    "ValidationResult",
    # PDF
    "generate_anmeldung_pdf",
    "transform_answers_to_pdf_format",
]
