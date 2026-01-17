"""Unit tests for prompts module."""

from voice_api.core import ANMELDUNG_FORM_FIELDS
from voice_api.llm import build_system_prompt


class TestBuildSystemPrompt:
    """Test system prompt building."""

    def test_system_prompt_is_string(self):
        """build_system_prompt should return a string."""
        prompt = build_system_prompt()
        assert isinstance(prompt, str)
        assert len(prompt) > 0

    def test_system_prompt_includes_all_field_labels(self):
        """System prompt should include all form field labels for field discovery."""
        prompt = build_system_prompt()

        for field in ANMELDUNG_FORM_FIELDS:
            assert field.label in prompt, f"Field '{field.label}' not found in prompt"

    def test_system_prompt_includes_all_field_descriptions(self):
        """System prompt should include field descriptions for user context."""
        prompt = build_system_prompt()

        for field in ANMELDUNG_FORM_FIELDS:
            assert field.description in prompt, f"Description for '{field.label}' not found in prompt"

    def test_system_prompt_includes_tool_names(self):
        """System prompt should reference the main tools for interaction."""
        prompt = build_system_prompt()
        assert "get_next_form_field" in prompt
        assert "validate_form_field" in prompt
        assert "save_form_field" in prompt
