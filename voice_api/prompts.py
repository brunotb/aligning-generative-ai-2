"""DEPRECATED: This module has been moved to voice_api.llm.

For backward compatibility, this re-exports from the new location.
All new code should import from voice_api.llm instead.

Deprecated::
    Use voice_api.llm instead:
    
    from voice_api.llm import build_system_prompt, SYSTEM_PROMPT_BASE
"""

from __future__ import annotations

# Re-export from new location for backward compatibility
from .llm.prompts import SYSTEM_PROMPT_BASE, build_system_prompt

__all__ = ["SYSTEM_PROMPT_BASE", "build_system_prompt"]
