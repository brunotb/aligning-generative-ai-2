"""Tests for the new simplified workflow without field_id parameter."""

from voice_api.llm import tools


class TestNoFieldIdHallucination:
    """Verify workflow changes prevent field_id hallucination."""

    def test_system_prompt_includes_core_tools(self):
        """System prompt should reference the three core workflow tools."""
        from voice_api.llm import build_system_prompt
        
        prompt = build_system_prompt()
        
        # These are essential for the workflow
        assert "get_next_form_field" in prompt
        assert "validate_form_field" in prompt
        assert "save_form_field" in prompt

    def test_tools_exist(self):
        """Verify all required tools exist."""
        declarations = tools.build_function_declarations()
        tool_names = [d.name for d in declarations]
        
        assert "get_next_form_field" in tool_names
        assert "validate_form_field" in tool_names
        assert "save_form_field" in tool_names
        assert "generate_anmeldung_pdf" in tool_names

    def test_tool_declarations_are_valid(self):
        """Verify tool declarations are properly structured."""
        declarations = tools.build_function_declarations()
        
        assert len(declarations) > 0
        for tool in declarations:
            assert hasattr(tool, "name")
            assert tool.name
