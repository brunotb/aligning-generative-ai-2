"""Standalone verification script for handler event emissions."""

import asyncio
import sys
from unittest.mock import MagicMock, patch

# --- MOCKING START ---
mock_vr_module = MagicMock()
mock_runner = MagicMock()
mock_runner.get_current_session_id.return_value = "test_session"
mock_vr_module.voice_runner = mock_runner
sys.modules["voice_api.api.voice_runner"] = mock_vr_module
# --- MOCKING END ---

from voice_api.app.state import FormState
try:
    from voice_api.llm.handlers import handle_tool_calls
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)

from voice_api.api.events import FormEvent

async def run_verification():
    print("Verifying save_form_field event emission...")
    
    # Setup
    form_state = FormState()
    session = MagicMock()
    
    # Make send_tool_response awaitable
    async def async_mock(*args, **kwargs):
        return None
    session.send_tool_response = MagicMock(side_effect=async_mock)
    
    # Mock event_emitter
    with patch("voice_api.llm.handlers.event_emitter") as mock_emitter:
        # Create MOCK tool call structure
        tool_call = MagicMock()
        fn_call = MagicMock()
        fn_call.name = "save_form_field"
        fn_call.args = {"value": "Mueller"}
        fn_call.id = "call_123"
        tool_call.function_calls = [fn_call]
        
        # Test
        await handle_tool_calls(tool_call, session, form_state)
        
        # Verify
        if not mock_emitter.emit_sync.called:
            print("FAIL: emit_sync was not called for save_form_field")
            sys.exit(1)
            
        event = mock_emitter.emit_sync.call_args[0][0]
        
        if event.type != "field_saved":
            print(f"FAIL: Expected event type 'field_saved', got '{event.type}'")
            sys.exit(1)
            
        if event.data.get("field_id") != "family_name_p1":
             print(f"FAIL: Expected field_id 'family_name_p1', got '{event.data.get('field_id')}'")
             sys.exit(1)

        print("PASS: save_form_field emitted 'field_saved'")

    print("\nVerifying update_previous_field event emission...")
    
    # Setup
    form_state = FormState()
    field_id = "family_name_p1"
    form_state.record_value(field_id, "OldValue")
    form_state.advance()
    
    session = MagicMock()
    session.send_tool_response = MagicMock(side_effect=async_mock)
    
    # Mock event_emitter
    with patch("voice_api.llm.handlers.event_emitter") as mock_emitter:
        # Create MOCK tool call
        tool_call = MagicMock()
        fn_call = MagicMock()
        fn_call.name = "update_previous_field"
        fn_call.args = {"field_id": field_id, "value": "NewValue"}
        fn_call.id = "call_456"
        tool_call.function_calls = [fn_call]
        
        # Test
        await handle_tool_calls(tool_call, session, form_state)
        
        # Verify
        if not mock_emitter.emit_sync.called:
            print("FAIL: emit_sync was not called for update_previous_field")
            sys.exit(1)
            
        event = mock_emitter.emit_sync.call_args[0][0]
        if event.type != "field_updated":
            print(f"FAIL: Expected event type 'field_updated', got '{event.type}'")
            sys.exit(1)
            
        if event.data.get("value") != "NewValue":
             print(f"FAIL: Expected value 'NewValue', got '{event.data.get('value')}'")
             sys.exit(1)
             
        print("PASS: update_previous_field emitted 'field_updated'")

if __name__ == "__main__":
    asyncio.run(run_verification())
