"""
PDF generation for Anmeldung form.

This module handles conversion of voice form answers to PDF format and generates
the filled PDF document. It maps voice field IDs to PDF field IDs and handles
necessary type conversions (e.g., string "0" to integer 0 for choice fields).
"""

from __future__ import annotations

import os
from typing import Dict, Optional, Any
from io import BytesIO
from datetime import datetime

from .anmeldung_fields import FIELD_BY_ID

# Path to the PDF template (relative to project root)
PDF_TEMPLATE_PATH = "documents/Anmeldung_Meldeschein_20220622.pdf"


def transform_answers_to_pdf_format(voice_answers: Dict[str, str]) -> Dict[str, Any]:
    """
    Transform voice form answers to PDF format.

    Maps voice field IDs to PDF field IDs and converts types as needed:
    - Integer choice fields: string "0" → integer 0
    - Text fields: passed as-is
    - Date fields: passed as-is (already in DD.MM.YYYY format)

    Args:
        voice_answers: Dictionary keyed by voice field_id
            Example: {
                "family_name_p1": "Mueller",
                "gender_p1": "0",
                "birth_date_p1": "15.01.1990"
            }

    Returns:
        Dictionary keyed by PDF field_id, ready for PyPDFForm
            Example: {
                "fam1": "Mueller",
                "geschl1": 0,
                "gebdat1": "15.01.1990"
            }

    Raises:
        KeyError: If a voice field_id is not found in the field definitions
    """
    pdf_data = {}

    for field_id, value in voice_answers.items():
        # Look up field definition
        field_def = FIELD_BY_ID.get(field_id)
        if not field_def:
            # Skip unknown fields silently
            continue

        pdf_field_id = field_def.pdf_field_id

        # Convert type based on validator type
        if field_def.validator.type == "integer_choice":
            try:
                pdf_data[pdf_field_id] = int(value)
            except ValueError:
                # If conversion fails, store as string
                pdf_data[pdf_field_id] = value
        else:
            # Text, date, postal code: store as-is
            pdf_data[pdf_field_id] = value

    return pdf_data


def generate_anmeldung_pdf(
    voice_answers: Dict[str, str], output_path: Optional[str] = None
) -> bytes:
    """
    Generate a filled Anmeldung PDF from voice form answers.

    Transforms voice answers to PDF format, fills the PDF template, and optionally
    saves it to disk. Returns the PDF bytes for further processing or transmission.

    Args:
        voice_answers: Form answers keyed by voice field_id
        output_path: Optional path to save the PDF file. If provided, the PDF is
            written to this location. The directory is created if it doesn't exist.

    Returns:
        PDF file as bytes (can be written to file or streamed to user)

    Raises:
        FileNotFoundError: If the PDF template cannot be found
        ImportError: If PyPDFForm is not installed
        ValueError: If transformation of answers fails
        Exception: If PDF filling fails
    """
    # Verify PyPDFForm is available
    try:
        from PyPDFForm import PdfWrapper
    except ImportError:
        raise ImportError(
            "PyPDFForm is required for PDF generation. "
            "Install it with: pip install PyPDFForm"
        )

    # Check that template exists
    if not os.path.exists(PDF_TEMPLATE_PATH):
        raise FileNotFoundError(
            f"PDF template not found at: {PDF_TEMPLATE_PATH}\n"
            f"Expected path: {os.path.abspath(PDF_TEMPLATE_PATH)}"
        )

    # Transform voice answers to PDF format
    try:
        pdf_data = transform_answers_to_pdf_format(voice_answers)
    except Exception as e:
        raise ValueError(f"Failed to transform form answers: {e}")

    # Fill the PDF
    try:
        pdf = PdfWrapper(PDF_TEMPLATE_PATH, use_full_widget_name=True)
        filled_pdf = pdf.fill(pdf_data)

        # Extract as bytes
        pdf_buffer = BytesIO()
        filled_pdf.write(pdf_buffer)
        pdf_buffer.seek(0)
        pdf_bytes = pdf_buffer.getvalue()
    except Exception as e:
        raise Exception(f"PDF filling failed: {e}\nMake sure all required fields are present in the data.")

    # Save to file if output path is provided
    if output_path:
        try:
            # Create directory if needed
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)

            # Write PDF
            with open(output_path, "wb") as f:
                f.write(pdf_bytes)
        except Exception as e:
            raise Exception(f"Failed to save PDF to {output_path}: {e}")

    return pdf_bytes
