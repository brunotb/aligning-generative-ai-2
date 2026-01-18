"""Test that handlers emit correct events for UI synchronization."""

import pytest
from unittest.mock import MagicMock, patch
from google.genai import types

from voice_api.app.state import FormState
from voice_api.llm.handlers import handle_tool_calls
from voice_api.api.events import FormEvent


@pytest.mark.asyncio
async def test_save_form_field_emits_event():
    """save_form_field should emit field_saved event."""
    # Setup
    form_state = FormState()
    session = MagicMock()
    session.send_tool_response = MagicMock()
    
    # Mock event_emitter
    with patch("voice_api.llm.handlers.event_emitter") as mock_emitter:
        # Create tool call
        tool_call = types.ToolCall(
            function_calls=[
                types.FunctionCall(
                    name="save_form_field",
                    args={"value": "Mueller"}, 
                    id="call_123"
                )
            ]
        )
        
        # Test
        await handle_tool_calls(tool_call, session, form_state)
        
        # Verify
        assert mock_emitter.emit_sync.called
        event = mock_emitter.emit_sync.call_args[0][0]
        assert isinstance(event, FormEvent)
        assert event.type == "field_saved"
        assert event.data["field_id"] == "family_name_p1"
        assert event.data["value"] == "Mueller"


@pytest.mark.asyncio
async def test_update_previous_field_emits_event():
    """update_previous_field should emit field_updated event."""
    # Setup
    form_state = FormState()
    # Pre-fill a field
    field_id = "family_name_p1"
    form_state.record_value(field_id, "OldValue")
    form_state.advance()
    
    session = MagicMock()
    session.send_tool_response = MagicMock()
    
    # Mock event_emitter
    with patch("voice_api.llm.handlers.event_emitter") as mock_emitter:
        # Create tool call
        tool_call = types.ToolCall(
            function_calls=[
                types.FunctionCall(
                    name="update_previous_field",
                    args={"field_id": field_id, "value": "NewValue"},
                    id="call_456"
                )
            ]
        )
        
        # Test
        await handle_tool_calls(tool_call, session, form_state)
        
        # Verify
        assert mock_emitter.emit_sync.called
        event = mock_emitter.emit_sync.call_args[0][0]
        assert isinstance(event, FormEvent)
        assert event.type == "field_updated"
        assert event.data["field_id"] == field_id
        assert event.data["value"] == "NewValue"
