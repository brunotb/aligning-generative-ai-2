"""Tests for the new simplified workflow without field_id parameter."""

from voice_api.llm import tools


class TestNoFieldIdHallucination:
    """Verify workflow changes prevent field_id hallucination."""

    def test_system_prompt_enforces_workflow(self):
        """System prompt should enforce the correct workflow sequence."""
        from voice_api.llm import build_system_prompt
        
        prompt = build_system_prompt()
        
        # Should mention the mandatory workflow
        assert "MANDATORY WORKFLOW" in prompt
        assert "get_next_form_field" in prompt
        assert "validate_form_field" in prompt
        assert "save_form_field" in prompt
        assert "CURRENT field" in prompt
        assert "Do NOT pass field_id" in prompt

    def test_tools_exist(self):
        """Verify all required tools exist."""
        declarations = tools.build_function_declarations()
        tool_names = [d.name for d in declarations]
        
        assert "get_next_form_field" in tool_names
        assert "validate_form_field" in tool_names
        assert "save_form_field" in tool_names
        assert "generate_anmeldung_pdf" in tool_names

    def test_validate_tool_description_mentions_current_field(self):
        """validate tool description should mention CURRENT field."""
        declarations = tools.build_function_declarations()
        validate_tool = next(d for d in declarations if d.name == "validate_form_field")
        
        # Description should guide model to use current field
        desc = validate_tool.description
        if desc:
            assert "CURRENT" in desc or "current" in desc

    def test_save_tool_description_mentions_current_field(self):
        """save tool description should mention CURRENT field."""
        declarations = tools.build_function_declarations()
        save_tool = next(d for d in declarations if d.name == "save_form_field")
        
        # Description should guide model to use current field
        desc = save_tool.description
        if desc:
            assert "CURRENT" in desc or "current" in desc
