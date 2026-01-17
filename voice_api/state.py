"""State management for the guided form flow."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .schema import FormField, FORM_FIELDS


@dataclass
class FormState:
    """Tracks form progress, answers, and errors."""

    fields: List[FormField] = field(default_factory=lambda: FORM_FIELDS.copy())
    current_index: int = 0
    answers: Dict[str, str] = field(default_factory=dict)
    validation_errors: Dict[str, str] = field(default_factory=dict)

    def current_field(self) -> Optional[FormField]:
        """Return the current field to collect, or None if finished."""
        if self.current_index < len(self.fields):
            return self.fields[self.current_index]
        return None

    def advance(self) -> Optional[FormField]:
        """Move to the next field and return it, or None if finished."""
        self.current_index += 1
        return self.current_field()

    def is_complete(self) -> bool:
        """Return True when all fields are collected."""
        return self.current_index >= len(self.fields)

    def record_value(self, field_id: str, value: str) -> None:
        """Persist a validated value and clear previous error."""
        self.answers[field_id] = value
        self.validation_errors.pop(field_id, None)

    def set_error(self, field_id: str, message: str) -> None:
        """Remember a validation error for a field."""
        self.validation_errors[field_id] = message

    def progress_percent(self) -> float:
        """Compute completion percentage."""
        total = len(self.fields)
        if total == 0:
            return 100.0
        return min(100.0, (len(self.answers) / total) * 100)
