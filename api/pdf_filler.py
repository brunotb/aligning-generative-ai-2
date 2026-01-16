import os
import re
from datetime import datetime
from typing import Dict, Optional
from PyPDFForm import PdfWrapper
from io import BytesIO


# =============================================================================
# VALIDATION CONSTANTS AND HELPERS
# =============================================================================

# Valid ranges for radio button fields (0-based indices)
GENDER_VALUES = {
    0: "M",      # Männlich
    1: "W",      # Weiblich
    2: "o.A.",   # ohne Angabe
    3: "D"       # Divers
}

FAMILY_STATUS_VALUES = {
    0: "LD",     # ledig
    1: "VH",     # verheiratet
    2: "VW",     # verwitwet
    3: "GS",     # geschieden
    4: "LP",     # eingetragene Lebenspartnerschaft
    5: "LV",     # Lebenspartner verstorben
    6: "LA",     # Lebenspartnerschaft aufgehoben
    7: "EA",     # Ehe aufgehoben
    8: "LE",     # Lebenspartner für tot erklärt
    9: "NB"      # nicht bekannt
}

RELIGION_VALUES = {
    0: "rk",     # Römisch-katholisch
    1: "ak",     # Altkatholisch
    2: "fa",     # Freie Religionsgemeinschaft Alzey
    3: "fb",     # Freireligiöse Landesgemeinde Baden
    4: "fg",     # Freireligiöse Landesgemeinde Pfalz
    5: "fm",     # Freireligiöse Gemeinde Mainz
    6: "fs",     # Freireligiöse Gemeinde Offenbach
    7: "sn",     # keiner steuererhebenden Religionsgemeinschaft angehörend
    8: "ev",     # Evangelisch
    9: "lt",     # Evangelisch-lutherisch
    10: "rf",    # Evangelisch-reformiert
    11: "fr",    # Französisch-reformiert
    12: "ib",    # Israelitische Religionsgemeinschaft Baden
    13: "iw",    # Israelitische Religionsgemeinschaft Württemberg
    14: "isby",  # Landesverband der israelitischen Kultusgemeinden in Bayern
    15: "ishe",  # Jüdische Gemeinde Frankfurt
    16: "il",    # Jüdische Gemeinden im Landesverband Hessen
    17: "isnw",  # Nordrhein-Westfalen: israelitisch (jüdisch)
    18: "jh",    # Jüdische Gemeinde Hamburg
    19: "isrp",  # Jüdische Kultusgemeinden Bad Kreuznach und Koblenz
    20: "issl",  # Saarland: israelitisch
    21: "oa"     # keiner öffentlich-rechtlichen Religionsgesellschaft angehörig
}

ID_TYPE_VALUES = {
    0: "PA",     # Personalausweis
    1: "RP",     # Reisepass
    2: "KRP",    # Kinderreisepass
    3: "KA"      # Kinderausweis
}

HOUSING_TYPE_VALUES = {
    0: "alleinige Wohnung",
    1: "Hauptwohnung",
    2: "Nebenwohnung"
}

# PDF template path (relative to the project root)
PDF_TEMPLATE_PATH = "documents/Anmeldung_Meldeschein_20220622.pdf"

# Required fields for each person (at least person 1 must be present)
REQUIRED_PERSON_FIELDS = {
    "fam": "Family name (Familienname)",
    "vorn": "First name(s) (Vorname)",
    "gebdat": "Date of birth (Geburtsdatum)",
    "gebort": "Place of birth (Geburtsort)",
    "geschl": "Gender (Geschlecht)",
    "famst": "Family status (Familienstand)",
    "staatsang": "Nationality (Staatsangehörigkeit)",
    "rel": "Religion (Religion)"
}

REQUIRED_MOVE_FIELDS = {
    "einzug": "Move-in date (Einzugsdatum)",
    "neuw.strasse": "New address street (Neue Wohnung Straße)",
    "nw.plz": "New address ZIP code (Neue Wohnung PLZ)",
    "wohnung": "Housing type (Wohnung type)"
}


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

def _validate_date_format(date_str: str, field_name: str) -> str:
    """
    Validate that a date is in DD.MM.YYYY format.
    
    Args:
        date_str: Date string to validate
        field_name: Name of the field for error messages
        
    Returns:
        The validated date string
        
    Raises:
        ValueError: If date format is invalid
    """
    if not date_str:
        raise ValueError(f"{field_name}: Date cannot be empty")
    
    # Check format with regex
    pattern = r"^\d{2}\.\d{2}\.\d{2}(?:\d{2})?$"
    if not re.match(pattern, date_str):
        raise ValueError(
            f"{field_name}: Invalid date format '{date_str}'. "
            f"Expected DD.MM.YYYY or DD.MM.YY format"
        )
    
    # Try to parse the date to ensure it's valid
    try:
        parts = date_str.split(".")
        day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
        
        # Handle 2-digit year
        if year < 100:
            year += 2000 if year <= 30 else 1900
        
        datetime(year, month, day)
    except (ValueError, IndexError):
        raise ValueError(
            f"{field_name}: Invalid date '{date_str}'. "
            f"Please ensure day (1-31), month (1-12), and year are valid"
        )
    
    return date_str


def _validate_integer_field(
    value: any,
    field_name: str,
    min_val: int = 0,
    max_val: int = None
) -> int:
    """
    Validate that a value is an integer within an acceptable range.
    
    Args:
        value: Value to validate
        field_name: Name of the field for error messages
        min_val: Minimum acceptable value (inclusive)
        max_val: Maximum acceptable value (inclusive)
        
    Returns:
        The validated integer value
        
    Raises:
        ValueError: If value is not valid
    """
    if value is None:
        raise ValueError(f"{field_name}: Value cannot be None")
    
    try:
        int_value = int(value)
    except (ValueError, TypeError):
        raise ValueError(
            f"{field_name}: Expected integer value, got {type(value).__name__}: {value}"
        )
    
    if int_value < min_val:
        raise ValueError(
            f"{field_name}: Value {int_value} is below minimum ({min_val})"
        )
    
    if max_val is not None and int_value > max_val:
        raise ValueError(
            f"{field_name}: Value {int_value} exceeds maximum ({max_val})"
        )
    
    return int_value


def _validate_gender(value: int, person_num: int) -> int:
    """
    Validate gender field (0-3).
    
    Args:
        value: Gender index
        person_num: Person number for error context
        
    Returns:
        The validated gender index
        
    Raises:
        ValueError: If gender value is invalid
    """
    gender_idx = _validate_integer_field(
        value,
        f"Person {person_num} Gender (geschl{person_num})",
        min_val=0,
        max_val=3
    )
    return gender_idx


def _validate_family_status(value: int, person_num: int) -> int:
    """
    Validate family status field (0-9).
    
    Args:
        value: Family status index
        person_num: Person number for error context
        
    Returns:
        The validated family status index
        
    Raises:
        ValueError: If family status value is invalid
    """
    famst_idx = _validate_integer_field(
        value,
        f"Person {person_num} Family Status (famst{person_num})",
        min_val=0,
        max_val=9
    )
    return famst_idx


def _validate_religion(value: int, person_num: int) -> int:
    """
    Validate religion field (0-21).
    
    Args:
        value: Religion index
        person_num: Person number for error context
        
    Returns:
        The validated religion index
        
    Raises:
        ValueError: If religion value is invalid
    """
    rel_idx = _validate_integer_field(
        value,
        f"Person {person_num} Religion (rel{person_num})",
        min_val=0,
        max_val=21
    )
    return rel_idx


def _validate_id_type(value: int, person_num: int) -> int:
    """
    Validate ID document type field.
    
    Args:
        value: ID type index
        person_num: Person number for error context
        
    Returns:
        The validated ID type index
        
    Raises:
        ValueError: If ID type value is invalid
    """
    art_idx = _validate_integer_field(
        value,
        f"Person {person_num} ID Type (art{person_num})",
        min_val=0,
        max_val=3
    )
    return art_idx


def _validate_housing_type(value: int) -> int:
    """
    Validate housing type field (0-2).
    
    Args:
        value: Housing type index
        
    Returns:
        The validated housing type index
        
    Raises:
        ValueError: If housing type value is invalid
    """
    wohnung_idx = _validate_integer_field(
        value,
        "Housing Type (wohnung)",
        min_val=0,
        max_val=2
    )
    return wohnung_idx


def _validate_string_field(value: str, field_name: str, min_length: int = 1) -> str:
    """
    Validate that a value is a non-empty string.
    
    Args:
        value: Value to validate
        field_name: Name of the field for error messages
        min_length: Minimum string length required
        
    Returns:
        The validated string value
        
    Raises:
        ValueError: If value is not valid
    """
    if value is None:
        raise ValueError(f"{field_name}: Value cannot be None")
    
    str_value = str(value).strip()
    
    if len(str_value) < min_length:
        raise ValueError(
            f"{field_name}: String is too short (minimum {min_length} characters). "
            f"Got: '{str_value}'"
        )
    
    return str_value


def _validate_person_data(person_data: Dict, person_num: int) -> None:
    """
    Validate all data for a single person.
    
    Args:
        person_data: Dictionary with person's data
        person_num: Person number (1-4)
        
    Raises:
        ValueError: If any required or format-invalid field is found
    """
    # Check required fields
    for field_key, field_label in REQUIRED_PERSON_FIELDS.items():
        pdf_key = f"{field_key}{person_num}"
        if pdf_key not in person_data or person_data[pdf_key] is None:
            raise ValueError(
                f"Person {person_num}: Required field missing: {field_label} ({pdf_key})"
            )
    
    # Validate individual fields
    suffix = str(person_num)
    
    # String fields
    _validate_string_field(
        person_data.get(f"fam{suffix}"),
        f"Person {person_num} Family Name (fam{suffix})"
    )
    _validate_string_field(
        person_data.get(f"vorn{suffix}"),
        f"Person {person_num} First Name (vorn{suffix})"
    )
    _validate_string_field(
        person_data.get(f"gebort{suffix}"),
        f"Person {person_num} Place of Birth (gebort{suffix})"
    )
    _validate_string_field(
        person_data.get(f"staatsang{suffix}"),
        f"Person {person_num} Nationality (staatsang{suffix})"
    )
    
    # Date fields
    _validate_date_format(
        person_data.get(f"gebdat{suffix}"),
        f"Person {person_num} Date of Birth (gebdat{suffix})"
    )
    
    # Integer fields with validation
    _validate_gender(person_data.get(f"geschl{suffix}"), person_num)
    _validate_family_status(person_data.get(f"famst{suffix}"), person_num)
    _validate_religion(person_data.get(f"rel{suffix}"), person_num)
    
    # Optional doctorate (empty string is allowed)
    if f"gr{suffix}" in person_data:
        gr_val = person_data.get(f"gr{suffix}", "")
        if gr_val and not isinstance(gr_val, str):
            raise ValueError(
                f"Person {person_num} Doctorate (gr{suffix}): "
                f"Expected string, got {type(gr_val).__name__}"
            )
    
    # Optional: marriage/partnership data if applicable
    famst_val = person_data.get(f"famst{suffix}")
    # If married (VH=1) or in partnership (LP=4), marriage date should be present
    if famst_val in [1, 4]:
        if f"dat{suffix}" not in person_data or not person_data.get(f"dat{suffix}"):
            raise ValueError(
                f"Person {person_num}: Marriage/Partnership date (dat{suffix}) "
                f"is required for family status '{FAMILY_STATUS_VALUES.get(famst_val, 'unknown')}'"
            )
        _validate_date_format(
            person_data.get(f"dat{suffix}"),
            f"Person {person_num} Marriage Date (dat{suffix})"
        )
    
    # Validate passport data if present
    if f"art{suffix}" in person_data:
        _validate_id_type(person_data.get(f"art{suffix}"), person_num)
        # If ID type is present, we should have ID details
        if f"serien{suffix}" in person_data:
            _validate_string_field(
                person_data.get(f"serien{suffix}"),
                f"Person {person_num} ID Series Number (serien{suffix})"
            )
        if f"ausstelldat{suffix}" in person_data:
            _validate_date_format(
                person_data.get(f"ausstelldat{suffix}"),
                f"Person {person_num} ID Issue Date (ausstelldat{suffix})"
            )
        if f"gueltig{suffix}" in person_data:
            _validate_date_format(
                person_data.get(f"gueltig{suffix}"),
                f"Person {person_num} ID Valid Until (gueltig{suffix})"
            )


def _validate_move_details(data: Dict) -> None:
    """
    Validate move/address related fields.
    
    Args:
        data: Complete form data
        
    Raises:
        ValueError: If any required move field is invalid
    """
    # Check required fields
    for field_key, field_label in REQUIRED_MOVE_FIELDS.items():
        if field_key not in data or data[field_key] is None:
            raise ValueError(
                f"Move Details: Required field missing: {field_label} ({field_key})"
            )
    
    # Validate individual fields
    _validate_date_format(
        data.get("einzug"),
        "Move-in Date (einzug)"
    )
    _validate_string_field(
        data.get("neuw.strasse"),
        "New Address Street (neuw.strasse)"
    )
    _validate_string_field(
        data.get("nw.plz"),
        "New Address ZIP Code (nw.plz)",
        min_length=4
    )
    _validate_housing_type(data.get("wohnung"))
    
    # Optional new city field
    if "nw.ort" in data:
        _validate_string_field(
            data.get("nw.ort"),
            "New Address City (nw.ort)"
        )
    
    # Previous address - if zuzug is present (moving from abroad), validate it
    if "zuzug" in data and data["zuzug"]:
        _validate_string_field(
            data.get("zuzug"),
            "Previous Address (zuzug) for Abroad Move"
        )
    else:
        # Previous address fields are optional
        if "bishwo.strasse" in data and data["bishwo.strasse"]:
            _validate_string_field(
                data.get("bishwo.strasse"),
                "Previous Address Street (bishwo.strasse)"
            )
        if "bishwo.plz" in data and data["bishwo.plz"]:
            _validate_string_field(
                data.get("bishwo.plz"),
                "Previous Address ZIP Code (bishwo.plz)"
            )


def _validate_separation_status(data: Dict) -> None:
    """
    Validate separation status fields.
    
    Args:
        data: Complete form data
        
    Raises:
        ValueError: If separation status fields are invalid
    """
    if "getrennt1" in data and data["getrennt1"] is not None:
        sep_val = _validate_integer_field(
            data.get("getrennt1"),
            "Separation Status (getrennt1)",
            min_val=0,
            max_val=1
        )


def _validate_signature_fields(data: Dict) -> None:
    """
    Validate signature location and date fields.
    
    Args:
        data: Complete form data
        
    Raises:
        ValueError: If signature fields are invalid
    """
    if "Ort1" in data and data["Ort1"]:
        _validate_string_field(
            data.get("Ort1"),
            "Signature Location (Ort1)"
        )
    
    if "Datum1" in data and data["Datum1"]:
        _validate_date_format(
            data.get("Datum1"),
            "Signature Date (Datum1)"
        )


def _validate_cross_field_rules(data: Dict) -> None:
    """
    Validate cross-field business rules and consistency.
    
    Args:
        data: Complete form data
        
    Raises:
        ValueError: If any cross-field rule is violated
    """
    # If person 1 is married/in partnership, and person 2 exists,
    # their family status should match
    if (f"famst1" in data and f"famst2" in data and 
        data.get("famst1") == data.get("famst2")):
        # If married, check marriage dates match (if both are present)
        if data.get("famst1") in [1, 4]:  # VH or LP
            dat1 = data.get("dat1")
            dat2 = data.get("dat2")
            if dat1 and dat2 and dat1 != dat2:
                raise ValueError(
                    "Marriage/Partnership Consistency: "
                    f"Person 1 and Person 2 have different marriage dates "
                    f"({dat1} vs {dat2}). Dates must match."
                )


def validate_anmeldung_data(data: Dict) -> Dict:
    """
    Validate all form data comprehensively.
    
    This is the master validation function that orchestrates all validation steps.
    
    Args:
        data: Dictionary containing all form data
        
    Returns:
        The validated data dictionary (if all validations pass)
        
    Raises:
        ValueError: With detailed error messages if validation fails
    """
    if not isinstance(data, dict):
        raise ValueError(
            f"Form data must be a dictionary, got {type(data).__name__}"
        )
    
    if not data:
        raise ValueError("Form data cannot be empty")
    
    errors = []
    
    try:
        _validate_move_details(data)
    except ValueError as e:
        errors.append(str(e))
    
    # Validate persons (at least person 1 must be present and valid)
    try:
        _validate_person_data(data, 1)
    except ValueError as e:
        errors.append(str(e))
    
    # Persons 2-4 are optional but if present, must be valid
    for person_num in [2, 3, 4]:
        try:
            # Check if any field for this person exists
            person_fields = [k for k in data.keys() if k.endswith(str(person_num))]
            if person_fields:
                _validate_person_data(data, person_num)
        except ValueError as e:
            errors.append(str(e))
    
    # Validate optional sections
    try:
        _validate_separation_status(data)
    except ValueError as e:
        errors.append(str(e))
    
    try:
        _validate_signature_fields(data)
    except ValueError as e:
        errors.append(str(e))
    
    # Validate cross-field rules
    try:
        _validate_cross_field_rules(data)
    except ValueError as e:
        errors.append(str(e))
    
    if errors:
        error_message = "Validation failed with the following errors:\n\n"
        for i, error in enumerate(errors, 1):
            error_message += f"{i}. {error}\n"
        raise ValueError(error_message)
    
    return data


# =============================================================================
# PDF FILLING FUNCTION
# =============================================================================

def fill_anmeldung_form(
    form_data: Dict,
    pdf_template_path: str = PDF_TEMPLATE_PATH,
    output_path: Optional[str] = None
) -> bytes:
    """
    Fills the Munich Residence Registration (Anmeldung) PDF form with provided data.
    
    This is the main public function that validates input data and generates a filled PDF.
    
    Args:
        form_data: Dictionary containing form data with keys matching the PDF fields.
                   Required keys:
                   - einzug: Move-in date (DD.MM.YYYY)
                   - neuw.strasse: New address street
                   - nw.plz: New address ZIP code
                   - wohnung: Housing type (0=single, 1=main, 2=secondary)
                   - fam1-4: Family names (at least fam1 required)
                   - vorn1-4: First names (at least vorn1 required)
                   - gebdat1-4: Birth dates (at least gebdat1 required)
                   - gebort1-4: Birth places (at least gebort1 required)
                   - geschl1-4: Gender codes (at least geschl1 required)
                   - famst1-4: Family status codes (at least famst1 required)
                   - staatsang1-4: Nationalities (at least staatsang1 required)
                   - rel1-4: Religion codes (at least rel1 required)
                   Optional keys:
                   - gr1-4: Academic degrees
                   - dat1-4: Marriage/partnership dates
                   - art1-4, serien1-4, ausstellb1-4, ausstelldat1-4, gueltig1-4: Passport data
                   - zuzug: Previous address if moving from abroad
                   - bishwo.strasse, bishwo.plz, bishwo.ort: Previous German address
                   - getrennt1: Separation status
                   - Ort1, Datum1: Signature location and date
        
        pdf_template_path: Path to the PDF template file (default: documents/Anmeldung_Meldeschein_20220622.pdf)
        
        output_path: Optional path to save the filled PDF. If provided, the PDF is saved to this location.
                     If not provided, the PDF is returned as bytes only.
        
    Returns:
        Bytes of the filled PDF document
        
    Raises:
        ValueError: If form data validation fails
        FileNotFoundError: If the PDF template cannot be found
        Exception: If PDF filling fails (e.g., due to missing fields)
        
    Example:
        >>> data = {
        ...     "einzug": "15.01.25",
        ...     "neuw.strasse": "Leopoldstraße 25 a",
        ...     "nw.plz": "80802",
        ...     "wohnung": 0,
        ...     "fam1": "von Gräfenberg",
        ...     "vorn1": "Maria-Luisa",
        ...     "gebdat1": "01.01.1990",
        ...     "gebort1": "São Paulo, Brasilien",
        ...     "geschl1": 1,
        ...     "famst1": 0,
        ...     "staatsang1": "Deutsch, Brasilianisch",
        ...     "rel1": 0,
        ...     "Ort1": "München",
        ...     "Datum1": "15.01.2025"
        ... }
        >>> pdf_bytes = fill_anmeldung_form(data)
        >>> # Or save to file:
        >>> fill_anmeldung_form(data, output_path="/path/to/output.pdf")
    """
    # Step 1: Validate all input data
    try:
        validated_data = validate_anmeldung_data(form_data)
    except ValueError as e:
        raise ValueError(f"Form validation failed: {str(e)}")
    
    # Step 2: Check if PDF template exists
    if not os.path.exists(pdf_template_path):
        raise FileNotFoundError(
            f"PDF template not found at: {pdf_template_path}\n"
            f"Please ensure the template exists at the specified path."
        )
    
    # Step 3: Load and fill the PDF
    try:
        pdf = PdfWrapper(pdf_template_path, use_full_widget_name=True)
        filled_pdf = pdf.fill(validated_data)
    except Exception as e:
        raise Exception(
            f"Failed to fill PDF: {str(e)}\n"
            f"This may indicate that a form field in the data does not exist in the template."
        )
    
    # Step 4: Get the PDF as bytes
    try:
        pdf_bytes = BytesIO()
        filled_pdf.write(pdf_bytes)
        pdf_bytes.seek(0)
        pdf_content = pdf_bytes.getvalue()
    except Exception as e:
        raise Exception(f"Failed to extract PDF bytes: {str(e)}")
    
    # Step 5: Save to file if output path is specified
    if output_path:
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(pdf_content)
        except Exception as e:
            raise Exception(
                f"Failed to save PDF to {output_path}: {str(e)}"
            )
    
    return pdf_content
