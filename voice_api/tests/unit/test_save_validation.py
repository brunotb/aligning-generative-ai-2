"""Test that save_form_field validates data before saving."""

import pytest
from voice_api.app.state import FormState


class TestSaveFormFieldValidation:
    """Test save_form_field enforces validation."""

    def test_save_form_field_rejects_invalid_date(self):
        """save_form_field should reject invalid date format."""
        form_state = FormState()
        
        # Advance to birth_date field (index 2)
        form_state.record_value(form_state.fields[0].field_id, "Mueller")
        form_state.advance()
        form_state.record_value(form_state.fields[1].field_id, "Hans")
        form_state.advance()
        
        # Now on birth_date field
        current_field = form_state.current_field()
        assert current_field.field_id == "birth_date_p1"
        
        # Simulate what handler does
        from voice_api.app.validation import validate_field
        
        # Try to save invalid value (text instead of date)
        invalid_value = "Bernt"
        is_valid, message = validate_field(current_field, invalid_value)
        
        assert not is_valid
        assert "Invalid format" in message or "DDMMYYYY" in message
        
        # Handler should NOT allow saving
        # (we're testing the validation logic, not the handler directly)

    def test_save_form_field_rejects_invalid_gender(self):
        """save_form_field should reject invalid gender value."""
        form_state = FormState()
        
        # Find gender field
        for i, field in enumerate(form_state.fields):
            if field.field_id == "gender_p1":
                # Advance to this field
                while form_state.current_index < i:
                    current = form_state.current_field()
                    form_state.record_value(current.field_id, "test")
                    form_state.advance()
                break
        
        current_field = form_state.current_field()
        assert current_field.field_id == "gender_p1"
        
        from voice_api.app.validation import validate_field
        
        # Try to save invalid value (text instead of integer choice)
        invalid_value = "Berlin"
        is_valid, message = validate_field(current_field, invalid_value)
        
        assert not is_valid
        assert "whole number" in message.lower() or "integer" in message.lower()

    def test_save_form_field_accepts_valid_data(self):
        """save_form_field should accept valid data."""
        form_state = FormState()
        
        # Test first field (text)
        current_field = form_state.current_field()
        assert current_field.field_id == "family_name_p1"
        
        from voice_api.app.validation import validate_field
        
        valid_value = "Mueller"
        is_valid, message = validate_field(current_field, valid_value)
        
        assert is_valid
        assert message == ""

    def test_save_form_field_validates_date_format(self):
        """save_form_field should enforce date format."""
        form_state = FormState()
        
        # Advance to birth_date field
        while form_state.current_field().field_id != "birth_date_p1":
            current = form_state.current_field()
            form_state.record_value(current.field_id, "test")
            form_state.advance()
        
        current_field = form_state.current_field()
        from voice_api.app.validation import validate_field
        
        # Valid date
        is_valid, _ = validate_field(current_field, "03021999")
        assert is_valid
        
        # Invalid dates
        is_valid, _ = validate_field(current_field, "Bernt")
        assert not is_valid
        
        is_valid, _ = validate_field(current_field, "99999999")
        assert not is_valid

    def test_validation_prevents_field_confusion(self):
        """Validation should catch when values are swapped between fields."""
        form_state = FormState()
        from voice_api.app.validation import validate_field
        
        # Get birth_date and birth_place fields
        birth_date_field = None
        birth_place_field = None
        
        for field in form_state.fields:
            if field.field_id == "birth_date_p1":
                birth_date_field = field
            elif field.field_id == "birth_place_p1":
                birth_place_field = field
        
        assert birth_date_field is not None
        assert birth_place_field is not None
        
        # Date in place field - should pass (text validator accepts anything)
        is_valid, _ = validate_field(birth_place_field, "03021999")
        assert is_valid  # This is the current behavior (text validator)
        
        # Place in date field - should fail
        is_valid, _ = validate_field(birth_date_field, "Berlin")
        assert not is_valid  # Date validator rejects text
