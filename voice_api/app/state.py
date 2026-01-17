"""
Form state management for the guided form workflow.

Manages the user's progress through the form, tracking:
- Current field being collected
- Collected answers
- Validation errors
- Progress percentage

The FormState is passed through the entire workflow (audio capture, model processing,
tool handling) to maintain a consistent view of the form's state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..core import ANMELDUNG_FORM_FIELDS, AnmeldungField, transform_answers_to_pdf_format


@dataclass
class FormState:
    """
    Tracks the user's progress through the form.

    Maintains the current position in the form, collected answers, and any
    validation errors encountered. Provides methods to navigate the form,
    record values, and convert to PDF format for document generation.

    Attributes:
        fields: List of all form fields to collect (ordered)
        current_index: Index of the current field being filled
        answers: Dictionary of field_id → user answer
        validation_errors: Dictionary of field_id → error message
    """

    fields: List[AnmeldungField] = field(default_factory=lambda: ANMELDUNG_FORM_FIELDS.copy())
    current_index: int = 0
    answers: Dict[str, str] = field(default_factory=dict)
    validation_errors: Dict[str, str] = field(default_factory=dict)

    def current_field(self) -> Optional[AnmeldungField]:
        """
        Return the current field to collect, or None if finished.

        Returns:
            The AnmeldungField at current_index, or None if we've passed the end
        """
        if self.current_index < len(self.fields):
            return self.fields[self.current_index]
        return None

    def advance(self) -> Optional[AnmeldungField]:
        """
        Move to the next field and return it, or None if finished.

        Returns:
            The next AnmeldungField, or None if form is complete
        """
        self.current_index += 1
        return self.current_field()

    def is_complete(self) -> bool:
        """
        Return True when all fields are collected.

        Returns:
            True if current_index >= len(fields)
        """
        return self.current_index >= len(self.fields)

    def record_value(self, field_id: str, value: str) -> None:
        """
        Persist a validated value and clear any previous error.

        Args:
            field_id: The field's unique identifier
            value: The validated value to store
        """
        self.answers[field_id] = value
        self.validation_errors.pop(field_id, None)

    def set_error(self, field_id: str, message: str) -> None:
        """
        Remember a validation error for a field.

        Args:
            field_id: The field's unique identifier
            message: Error message to display to user
        """
        self.validation_errors[field_id] = message

    def progress_percent(self) -> float:
        """
        Compute completion percentage (0.0 to 100.0).

        Returns:
            Percentage of fields that have been answered
        """
        total = len(self.fields)
        if total == 0:
            return 100.0
        return min(100.0, (len(self.answers) / total) * 100)

    def to_pdf_format(self) -> Dict[str, Any]:
        """
        Convert collected answers to PDF field format.

        Transforms the voice form answers (keyed by voice field_id) to PDF format
        (keyed by pdf_field_id). Also handles type conversions needed for the PDF
        (e.g., string "0" to integer 0 for choice fields).

        Returns:
            Dictionary keyed by pdf_field_id, ready for PDF generation

        Raises:
            ImportError: If pdf_generator module cannot be imported
            ValueError: If transformation fails
        """
        return transform_answers_to_pdf_format(self.answers)
