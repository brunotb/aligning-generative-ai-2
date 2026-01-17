"""DEPRECATED: This module has been moved to voice_api.core.

For backward compatibility, this re-exports from the new location.
All new code should import from voice_api.core instead.

Deprecated::
    Use voice_api.core instead:
    
    from voice_api.core import generate_anmeldung_pdf, transform_answers_to_pdf_format
"""

from __future__ import annotations

# Re-export from new location for backward compatibility
from .core.pdf_generator import generate_anmeldung_pdf, transform_answers_to_pdf_format
__all__ = ["generate_anmeldung_pdf", "transform_answers_to_pdf_format"]
