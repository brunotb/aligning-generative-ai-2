"""Form schema definitions and catalog."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class FormField:
    """Definition of a form field exposed to the model."""

    field_id: str
    label: str
    description: str
    field_type: str  # e.g., text, date, postal_code
    required: bool = True
    examples: Optional[List[str]] = None
    constraints: Optional[Dict[str, str]] = None  # regex, min/max, etc.


# Initial catalog: extend to ~30 fields as needed
FORM_FIELDS: List[FormField] = [
    FormField(
        field_id="name",
        label="Full name",
        description="Your full legal name as on your ID",
        field_type="text",
        examples=["Jane Doe", "Max Mustermann"],
    ),
    FormField(
        field_id="date_of_move",
        label="Date of move",
        description="Date you moved into the residence (YYYY-MM-DD)",
        field_type="date",
        constraints={"format": "YYYY-MM-DD"},
    ),
    FormField(
        field_id="street",
        label="Street",
        description="Street and house number",
        field_type="text",
        examples=["Main Street 12", "Sonnenallee 5"],
    ),
    FormField(
        field_id="postal_code",
        label="Postal code",
        description="Five-digit German postal code",
        field_type="postal_code",
        constraints={"regex": "^\\d{5}$"},
    ),
    FormField(
        field_id="city",
        label="City",
        description="City or municipality",
        field_type="text",
        examples=["Munich", "Berlin"],
    ),
    FormField(
        field_id="previous_address",
        label="Previous address",
        description="Your previous address (street, postal code, city)",
        field_type="text",
        required=False,
    ),
]
