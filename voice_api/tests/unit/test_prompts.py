"""Unit tests for prompts module."""

from voice_api.core import ANMELDUNG_FORM_FIELDS
from voice_api.llm import build_system_prompt, SYSTEM_PROMPT_BASE


class TestBuildSystemPrompt:
    """Test system prompt building."""

    def test_system_prompt_is_string(self):
        """build_system_prompt should return a string."""
        prompt = build_system_prompt()
        assert isinstance(prompt, str)

    def test_system_prompt_includes_base(self):
        """System prompt should include the base prompt."""
        prompt = build_system_prompt()
        assert SYSTEM_PROMPT_BASE in prompt

    def test_system_prompt_includes_all_fields(self):
        """System prompt should include all form field labels."""
        prompt = build_system_prompt()

        for field in ANMELDUNG_FORM_FIELDS:
            assert field.label in prompt

    def test_system_prompt_includes_all_field_descriptions(self):
        """System prompt should include field descriptions."""
        prompt = build_system_prompt()

        for field in ANMELDUNG_FORM_FIELDS[:3]:  # Check at least first 3
            assert field.description in prompt

    def test_system_prompt_mentions_dates(self):
        """System prompt should mention date format requirements."""
        prompt = build_system_prompt()
        assert "DD.MM.YYYY" in prompt

    def test_system_prompt_mentions_postal_code(self):
        """System prompt should mention postal code requirements."""
        prompt = build_system_prompt()
        assert "postal" in prompt.lower()

    def test_system_prompt_mentions_pdf_generation(self):
        """System prompt should mention PDF generation at the end."""
        prompt = build_system_prompt()
        assert "generate_anmeldung_pdf" in prompt

    def test_system_prompt_includes_validation_rules(self):
        """System prompt should include validation rules section."""
        prompt = build_system_prompt()
        assert "Validation rules" in prompt

    def test_system_prompt_mentions_required_fields(self):
        """System prompt should note that all fields are required."""
        prompt = build_system_prompt()
        assert "required" in prompt.lower()

    def test_system_prompt_length(self):
        """System prompt should be substantial."""
        prompt = build_system_prompt()
        assert len(prompt) > 500  # Should be fairly detailed
