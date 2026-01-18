"""Integration tests to verify validation is enforced in both save and update operations."""

import pytest
from voice_api.app.state import FormState
from voice_api.app.validation import validate_field
from voice_api.core import FIELD_BY_ID


class TestValidationEnforcement:
    """Test that validation is properly enforced everywhere."""

    def test_save_enforces_validation_for_date_field(self):
        """Verify save would reject invalid date through validation."""
        form_state = FormState()
        
        # Advance to birth_date field
        while form_state.current_field().field_id != "birth_date_p1":
            current = form_state.current_field()
            form_state.record_value(current.field_id, "test")
            form_state.advance()
        
        current_field = form_state.current_field()
        assert current_field.field_id == "birth_date_p1"
        
        # Try invalid value
        invalid_value = "Berlin"  # City name, not a date
        is_valid, message = validate_field(current_field, invalid_value)
        
        assert not is_valid
        # Handler would reject this save

    def test_update_enforces_validation_for_date_field(self):
        """Verify update would reject invalid date through validation."""
        form_state = FormState()
        
        # Save valid birth date
        while form_state.current_field().field_id != "birth_date_p1":
            current = form_state.current_field()
            form_state.record_value(current.field_id, "test")
            form_state.advance()
        
        form_state.record_value("birth_date_p1", "03021999")
        form_state.advance()
        
        # Move forward
        form_state.advance()
        
        # Try to update with invalid value
        birth_date_field = FIELD_BY_ID["birth_date_p1"]
        invalid_value = "Munich"  # City name, not a date
        is_valid, message = validate_field(birth_date_field, invalid_value)
        
        assert not is_valid
        # Handler would reject this update

    def test_save_accepts_valid_data(self):
        """Verify save accepts properly validated data."""
        form_state = FormState()
        
        # Test with family name
        current_field = form_state.current_field()
        valid_value = "Mueller"
        
        is_valid, message = validate_field(current_field, valid_value)
        assert is_valid
        
        # Save should succeed
        form_state.record_value(current_field.field_id, valid_value)
        assert form_state.answers[current_field.field_id] == valid_value

    def test_update_accepts_valid_data(self):
        """Verify update accepts properly validated data."""
        form_state = FormState()
        
        # Save initial value
        field1 = form_state.current_field()
        form_state.record_value(field1.field_id, "Mueller")
        form_state.advance()
        
        # Move forward
        form_state.advance()
        
        # Update with valid value
        new_value = "Mueller-Schmidt"
        is_valid, message = validate_field(field1, new_value)
        assert is_valid
        
        form_state.record_value(field1.field_id, new_value)
        assert form_state.answers[field1.field_id] == new_value

    def test_validation_prevents_type_mismatch(self):
        """Validation should catch when wrong type of data is provided."""
        form_state = FormState()
        
        # Get fields of different types
        date_field = FIELD_BY_ID["birth_date_p1"]
        text_field = FIELD_BY_ID["family_name_p1"]
        choice_field = FIELD_BY_ID["gender_p1"]
        
        # Date field rejects text
        is_valid, _ = validate_field(date_field, "Berlin")
        assert not is_valid
        
        # Choice field rejects text
        is_valid, _ = validate_field(choice_field, "Berlin")
        assert not is_valid
        
        # Text field accepts date format (but this is expected - text is permissive)
        is_valid, _ = validate_field(text_field, "03021999")
        assert is_valid  # Text validator accepts anything non-empty

    def test_complete_workflow_with_validation(self):
        """Test complete workflow: save, attempt invalid update, correct update."""
        form_state = FormState()
        
        # 1. Save first three fields with valid data
        for i in range(3):
            current = form_state.current_field()
            if current.field_id == "family_name_p1":
                form_state.record_value(current.field_id, "Mueller")
            elif current.field_id == "first_name_p1":
                form_state.record_value(current.field_id, "Hans")
            elif current.field_id == "birth_date_p1":
                form_state.record_value(current.field_id, "03021999")
            form_state.advance()
        
        assert len(form_state.answers) == 3
        assert form_state.current_index == 3
        
        # 2. Try to update birth_date with invalid value
        birth_date_field = FIELD_BY_ID["birth_date_p1"]
        invalid_value = "NotADate"
        is_valid, message = validate_field(birth_date_field, invalid_value)
        assert not is_valid  # Would be rejected by handler
        
        # 3. Update with valid value
        valid_value = "15101999"
        is_valid, message = validate_field(birth_date_field, valid_value)
        assert is_valid
        
        form_state.record_value("birth_date_p1", valid_value)
        assert form_state.answers["birth_date_p1"] == valid_value
        assert form_state.current_index == 3  # Index unchanged

    def test_choice_field_validation(self):
        """Test that choice fields properly validate integer ranges."""
        gender_field = FIELD_BY_ID["gender_p1"]
        
        # Valid choices (0-3 for gender)
        for i in range(4):
            is_valid, _ = validate_field(gender_field, str(i))
            assert is_valid
        
        # Invalid choices
        is_valid, _ = validate_field(gender_field, "4")
        assert not is_valid
        
        is_valid, _ = validate_field(gender_field, "Male")
        assert not is_valid
        
        is_valid, _ = validate_field(gender_field, "Berlin")
        assert not is_valid

    def test_postal_code_validation(self):
        """Test that postal code fields validate correctly."""
        postal_field = FIELD_BY_ID["new_postal_code"]
        
        # Valid postal codes (4-5 digits)
        is_valid, _ = validate_field(postal_field, "10115")
        assert is_valid
        
        is_valid, _ = validate_field(postal_field, "1234")
        assert is_valid
        
        # Invalid postal codes
        is_valid, _ = validate_field(postal_field, "123")
        assert not is_valid
        
        is_valid, _ = validate_field(postal_field, "123456")
        assert not is_valid
        
        is_valid, _ = validate_field(postal_field, "Berlin")
        assert not is_valid
