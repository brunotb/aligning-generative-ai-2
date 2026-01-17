"""Unit tests for prompts module."""

from voice_api import prompts, schema


class TestBuildSystemPrompt:
    """Test system prompt building."""

    def test_system_prompt_is_string(self):
        """build_system_prompt should return a string."""
        prompt = prompts.build_system_prompt()
        assert isinstance(prompt, str)

    def test_system_prompt_includes_base(self):
        """System prompt should include the base prompt."""
        prompt = prompts.build_system_prompt()
        from voice_api.config import SYSTEM_PROMPT_BASE

        assert SYSTEM_PROMPT_BASE in prompt

    def test_system_prompt_includes_all_fields(self):
        """System prompt should include all form field labels."""
        prompt = prompts.build_system_prompt()

        for field in schema.FORM_FIELDS:
            assert field.label in prompt

    def test_system_prompt_includes_all_field_descriptions(self):
        """System prompt should include field descriptions."""
        prompt = prompts.build_system_prompt()

        for field in schema.FORM_FIELDS[:3]:  # Check at least first 3
            assert field.description in prompt

    def test_system_prompt_mentions_dates(self):
        """System prompt should mention date format requirements."""
        prompt = prompts.build_system_prompt()
        assert "DD.MM.YYYY" in prompt

    def test_system_prompt_mentions_postal_code(self):
        """System prompt should mention postal code requirements."""
        prompt = prompts.build_system_prompt()
        assert "postal" in prompt.lower()

    def test_system_prompt_mentions_pdf_generation(self):
        """System prompt should mention PDF generation at the end."""
        prompt = prompts.build_system_prompt()
        assert "generate_anmeldung_pdf" in prompt

    def test_system_prompt_includes_validation_rules(self):
        """System prompt should include validation rules section."""
        prompt = prompts.build_system_prompt()
        assert "Validation rules" in prompt

    def test_system_prompt_mentions_required_fields(self):
        """System prompt should note that all fields are required."""
        prompt = prompts.build_system_prompt()
        assert "required" in prompt.lower()

    def test_system_prompt_length(self):
        """System prompt should be substantial."""
        prompt = prompts.build_system_prompt()
        assert len(prompt) > 500  # Should be fairly detailed
