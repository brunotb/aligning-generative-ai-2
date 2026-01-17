"""
Complete field definitions for the Anmeldung (Munich residence registration) voice form.

This is the SINGLE SOURCE OF TRUTH for all form fields. Each field is defined with:
- Unique voice field ID
- Corresponding PDF field ID (for export)
- Human-readable label and description
- Validator type and configuration
- Enum values (for choice fields)
- Examples

All data for the form flow is derived from the definitions in this file.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, List, Any


@dataclass
class FieldValidator:
    """Configuration for how a field should be validated."""

    type: str  # "text", "date_de", "integer_choice", "postal_code_de"
    config: Optional[Dict[str, Any]] = None  # Validator-specific config (min, max, format, etc.)

    def __post_init__(self):
        """Normalize config to empty dict if None."""
        if self.config is None:
            self.config = {}


@dataclass
class AnmeldungField:
    """
    Definition of a single form field in the Anmeldung process.

    Attributes:
        field_id: Unique voice-friendly identifier (e.g., "family_name_p1")
        pdf_field_id: Corresponding PDF form field name (e.g., "fam1")
        label: Short human-readable label for display (e.g., "Family name")
        description: Detailed description explaining what to enter (from pdf_fields.json)
        validator: FieldValidator instance with type and config
        examples: List of valid example inputs
        required: Whether field is mandatory
        enum_values: Optional mapping of integer indices to human-readable labels (for choice fields)
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
# PERSON 1 FIELDS (Required)
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
        "Your date of birth in German format (day.month.year). "
        "Example: 15.01.1990"
    ),
    validator=FieldValidator(type="date_de", config={"format": "DD.MM.YYYY"}),
    examples=["15.01.1990", "01.12.1985"],
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
# MOVE DETAILS (Required)
# ============================================================================

MOVE_IN_DATE = AnmeldungField(
    field_id="move_in_date",
    pdf_field_id="einzug",
    label="Move-in date",
    description="Date you moved into the new residence (DD.MM.YYYY). Example: 15.01.2025",
    validator=FieldValidator(type="date_de", config={"format": "DD.MM.YYYY"}),
    examples=["15.01.2025", "01.02.2025"],
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
# FORM FIELD COLLECTION & LOOKUP MAPS
# ============================================================================

ANMELDUNG_FORM_FIELDS: List[AnmeldungField] = [
    # Person 1 details
    FAMILY_NAME_P1,
    FIRST_NAME_P1,
    BIRTH_DATE_P1,
    BIRTH_PLACE_P1,
    GENDER_P1,
    FAMILY_STATUS_P1,
    NATIONALITY_P1,
    RELIGION_P1,
    # Move details
    MOVE_IN_DATE,
    NEW_STREET_ADDRESS,
    NEW_POSTAL_CODE,
    NEW_CITY,
    HOUSING_TYPE,
]

# Build lookup maps for fast access
FIELD_BY_ID: Dict[str, AnmeldungField] = {
    field.field_id: field for field in ANMELDUNG_FORM_FIELDS
}
"""Lookup field by voice field_id."""

FIELD_BY_PDF_ID: Dict[str, AnmeldungField] = {
    field.pdf_field_id: field for field in ANMELDUNG_FORM_FIELDS
}
"""Lookup field by PDF field_id."""
