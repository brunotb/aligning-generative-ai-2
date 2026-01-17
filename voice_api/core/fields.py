"""
Form field definitions for Anmeldung (Munich residence registration).

This module is the SINGLE SOURCE OF TRUTH for all form fields in the voice API.
It contains complete field metadata including validation rules, descriptions, and examples.

All other modules should derive their field information from ANMELDUNG_FORM_FIELDS
or use the lookup maps FIELD_BY_ID / FIELD_BY_PDF_ID for efficient access.

Field definitions include:
- field_id: Unique voice-friendly identifier (e.g., "family_name_p1")
- pdf_field_id: Corresponding PDF form field name (e.g., "fam1")
- label: Short human-readable label for UI display
- description: Detailed explanation of what to enter
- validator: FieldValidator with type and configuration
- examples: Valid example inputs for guidance
- enum_values: For choice fields, maps indices to human-readable labels
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class FieldValidator:
    """
    Configuration for field validation.

    Attributes:
        type: Validator type ("text", "date_de", "integer_choice", "postal_code_de")
        config: Validator-specific configuration (e.g., min/max for choices)
    """

    type: str
    config: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        """Ensure config is always a dict."""
        if self.config is None:
            self.config = {}


@dataclass
class AnmeldungField:
    """
    Definition of a form field in the Anmeldung process.

    Attributes:
        field_id: Unique voice-friendly identifier for internal use
        pdf_field_id: PDF form field name for document generation
        label: Short label for user-facing displays
        description: Detailed explanation of the field
        validator: FieldValidator specifying how to validate input
        examples: List of valid example inputs
        required: Whether field is mandatory (default: True)
        enum_values: Optional dict mapping choice indices to display strings
    """

    field_id: str
    pdf_field_id: str
    label: str
    description: str
    validator: FieldValidator
    examples: List[str]
    required: bool = True
    enum_values: Optional[Dict[int, str]] = None


# ============================================================================
# PERSON 1 FIELDS (Required demographics and identification)
# ============================================================================

FAMILY_NAME_P1 = AnmeldungField(
    field_id="family_name_p1",
    pdf_field_id="fam1",
    label="Family name",
    description=(
        "Your full legal current family name including all name components. "
        "Example: Mueller, von Gräfenberg, López García"
    ),
    validator=FieldValidator(type="text"),
    examples=["Mueller", "von Gräfenberg", "López García"],
)

FIRST_NAME_P1 = AnmeldungField(
    field_id="first_name_p1",
    pdf_field_id="vorn1",
    label="First name(s)",
    description=(
        "Your first name(s) as officially registered. If multiple names, you can mark the primary one. "
        "Example: Maria, Johann, Maria-Luisa"
    ),
    validator=FieldValidator(type="text"),
    examples=["Maria", "Johann", "Maria-Luisa"],
)

BIRTH_DATE_P1 = AnmeldungField(
    field_id="birth_date_p1",
    pdf_field_id="gebdat1",
    label="Date of birth",
    description=(
        "Your date of birth (DDMMYY format - day, month, year without separators). "
        "Example: 150190 for January 15, 1990"
    ),
    validator=FieldValidator(type="date_de", config={"format": "DDMMYY"}),
    examples=["150190", "011285"],
)

BIRTH_PLACE_P1 = AnmeldungField(
    field_id="birth_place_p1",
    pdf_field_id="gebort1",
    label="Place of birth",
    description=(
        "City, region/district; if born abroad, include country. "
        "Example: Berlin, München Bayern, São Paulo Brasilien"
    ),
    validator=FieldValidator(type="text"),
    examples=["Berlin", "München, Bayern", "São Paulo, Brasilien"],
)

GENDER_P1 = AnmeldungField(
    field_id="gender_p1",
    pdf_field_id="geschl1",
    label="Gender",
    description="Your gender (choose one: 0=Male, 1=Female, 2=No answer, 3=Diverse)",
    validator=FieldValidator(type="integer_choice", config={"min": 0, "max": 3}),
    examples=["0", "1", "3"],
    enum_values={
        0: "M (Male / Männlich)",
        1: "W (Female / Weiblich)",
        2: "o.A. (No answer / ohne Angabe)",
        3: "D (Diverse)",
    },
)

FAMILY_STATUS_P1 = AnmeldungField(
    field_id="family_status_p1",
    pdf_field_id="famst1",
    label="Family status",
    description=(
        "Your legal family status (choose one): "
        "0=single, 1=married, 2=widowed, 3=divorced, "
        "4=registered partnership, 5=partner deceased, "
        "6=partnership dissolved, 7=marriage annulled, 8=partner declared dead, 9=unknown"
    ),
    validator=FieldValidator(type="integer_choice", config={"min": 0, "max": 9}),
    examples=["0", "1"],
    enum_values={
        0: "LD (Single / ledig)",
        1: "VH (Married / verheiratet)",
        2: "VW (Widowed / verwitwet)",
        3: "GS (Divorced / geschieden)",
        4: "LP (Registered partnership / Lebenspartnerschaft)",
        5: "LV (Partner deceased / Lebenspartner verstorben)",
        6: "LA (Partnership dissolved / Lebenspartnerschaft aufgehoben)",
        7: "EA (Marriage annulled / Ehe aufgehoben)",
        8: "LE (Partner declared dead / Lebenspartner für tot erklärt)",
        9: "NB (Unknown / nicht bekannt)",
    },
)

NATIONALITY_P1 = AnmeldungField(
    field_id="nationality_p1",
    pdf_field_id="staatsang1",
    label="Nationality",
    description=(
        "Your nationality (if multiple nationalities, list all; if stateless, note 'stateless'). "
        "Example: German, German and Brazilian, Stateless"
    ),
    validator=FieldValidator(type="text"),
    examples=["German", "German, Brazilian", "Stateless"],
)

RELIGION_P1 = AnmeldungField(
    field_id="religion_p1",
    pdf_field_id="rel1",
    label="Religion",
    description=(
        "Your religious affiliation (choose one): "
        "0=Roman Catholic, 1=Old Catholic, 8=Protestant, 9=Lutheran, "
        "21=None (no public religious organization), 22=Other"
    ),
    validator=FieldValidator(type="integer_choice", config={"min": 0, "max": 22}),
    examples=["0", "8", "21"],
    enum_values={
        0: "rk (Roman Catholic / Römisch-katholisch)",
        1: "ak (Old Catholic / Altkatholisch)",
        8: "ev (Protestant / Evangelisch)",
        9: "lt (Lutheran / Evangelisch-lutherisch)",
        21: "oa (None / keiner öffentlich-rechtlichen Religionsgesellschaft angehörig)",
        22: "other (Other / Sonstiges)",
    },
)

# ============================================================================
# MOVE DETAILS (Required - information about the new residence)
# ============================================================================

MOVE_IN_DATE = AnmeldungField(
    field_id="move_in_date",
    pdf_field_id="einzug",
    label="Move-in date",
    description=(
        "Date you moved into the new residence (DDMMYY format). "
        "Example: 150125 for January 15, 2025"
    ),
    validator=FieldValidator(type="date_de", config={"format": "DDMMYY"}),
    examples=["150125", "010225"],
)

NEW_STREET_ADDRESS = AnmeldungField(
    field_id="new_street_address",
    pdf_field_id="neuw.strasse",
    label="New address (street)",
    description=(
        "Street name, house number, and floor/apartment if applicable. "
        "Example: Leopoldstraße 25a, Sonnenallee 5 3. Stock"
    ),
    validator=FieldValidator(type="text"),
    examples=["Leopoldstraße 25 a", "Sonnenallee 5, 3. Stock"],
)

NEW_POSTAL_CODE = AnmeldungField(
    field_id="new_postal_code",
    pdf_field_id="nw.plz",
    label="Postal code",
    description="5-digit German postal code (PLZ). Example: 80802, 10115",
    validator=FieldValidator(
        type="postal_code_de", config={"min_digits": 4, "max_digits": 5}
    ),
    examples=["80802", "10115"],
)

NEW_CITY = AnmeldungField(
    field_id="new_city",
    pdf_field_id="nw.ort",
    label="City",
    description="City or municipality name. Example: München, Berlin",
    validator=FieldValidator(type="text"),
    examples=["München", "Berlin"],
)

HOUSING_TYPE = AnmeldungField(
    field_id="housing_type",
    pdf_field_id="wohnung",
    label="Housing type",
    description=(
        "Type of residence (choose one): "
        "0=sole residence (only apartment in Germany), "
        "1=main residence (primary residence), "
        "2=secondary residence (additional apartment)"
    ),
    validator=FieldValidator(type="integer_choice", config={"min": 0, "max": 2}),
    examples=["0", "1"],
    enum_values={
        0: "alleinige Wohnung (Sole residence)",
        1: "Hauptwohnung (Main residence)",
        2: "Nebenwohnung (Secondary residence)",
    },
)

# ============================================================================
# COMPLETE FORM FIELDS LIST & LOOKUP MAPS
# ============================================================================

ANMELDUNG_FORM_FIELDS: List[AnmeldungField] = [
    # Person 1 details (demographics and identification)
    FAMILY_NAME_P1,
    FIRST_NAME_P1,
    BIRTH_DATE_P1,
    BIRTH_PLACE_P1,
    GENDER_P1,
    FAMILY_STATUS_P1,
    NATIONALITY_P1,
    RELIGION_P1,
    # Move details (new residence information)
    MOVE_IN_DATE,
    NEW_STREET_ADDRESS,
    NEW_POSTAL_CODE,
    NEW_CITY,
    HOUSING_TYPE,
]
"""
Complete, ordered list of all form fields for the Anmeldung process.

Fields are presented in this order during the guided form flow.
This is the source of truth for all field definitions.
"""

# Fast lookup maps for field access
FIELD_BY_ID: Dict[str, AnmeldungField] = {
    field.field_id: field for field in ANMELDUNG_FORM_FIELDS
}
"""Map voice field_id to AnmeldungField definition."""

FIELD_BY_PDF_ID: Dict[str, AnmeldungField] = {
    field.pdf_field_id: field for field in ANMELDUNG_FORM_FIELDS
}
"""Map PDF field_id to AnmeldungField definition."""
