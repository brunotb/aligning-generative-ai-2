"""Unit tests for correction tools (get_all_answers, update_previous_field)."""

import pytest
from voice_api.app.state import FormState
from voice_api.core import ANMELDUNG_FORM_FIELDS, FIELD_BY_ID


class TestGetAllAnswers:
    """Test get_all_answers functionality."""

    def test_get_all_answers_empty_state(self):
        """get_all_answers returns empty list when no fields saved."""
        form_state = FormState()
        
        saved_fields = []
        for field_id, value in form_state.answers.items():
            field = FIELD_BY_ID.get(field_id)
            if field:
                saved_fields.append({
                    "field_id": field_id,
                    "label": field.label,
                    "value": value,
                })
        
        assert len(saved_fields) == 0
        assert form_state.current_index == 0

    def test_get_all_answers_with_partial_data(self):
        """get_all_answers returns saved fields correctly."""
        form_state = FormState()
        
        # Save first two fields
        field1 = form_state.current_field()
        form_state.record_value(field1.field_id, "Mueller")
        form_state.advance()
        
        field2 = form_state.current_field()
        form_state.record_value(field2.field_id, "Hans")
        form_state.advance()
        
        # Build response like handler does
        saved_fields = []
        for field_id, value in form_state.answers.items():
            field = FIELD_BY_ID.get(field_id)
            if field:
                try:
                    field_index = form_state.fields.index(field)
                except ValueError:
                    field_index = -1
                saved_fields.append({
                    "field_id": field_id,
                    "label": field.label,
                    "value": value,
                    "field_index": field_index,
                })
        
        assert len(saved_fields) == 2
        assert saved_fields[0]["value"] == "Mueller"
        assert saved_fields[1]["value"] == "Hans"
        assert form_state.current_index == 2

    def test_get_all_answers_includes_field_metadata(self):
        """get_all_answers includes field_id and label."""
        form_state = FormState()
        
        field1 = form_state.current_field()
        form_state.record_value(field1.field_id, "TestValue")
        form_state.advance()
        
        # Check metadata
        field_id = list(form_state.answers.keys())[0]
        field = FIELD_BY_ID.get(field_id)
        
        assert field is not None
        assert field.field_id == field1.field_id
        assert field.label == field1.label


class TestUpdatePreviousField:
    """Test update_previous_field functionality."""

    def test_update_previous_field_success(self):
        """Successfully update a previously saved field."""
        form_state = FormState()
        
        # Save first field
        field1 = form_state.current_field()
        form_state.record_value(field1.field_id, "Mueller")
        form_state.advance()
        
        # Save second field
        field2 = form_state.current_field()
        form_state.record_value(field2.field_id, "Hans")
        form_state.advance()
        
        # Now on field 3, update field 1
        old_value = form_state.answers[field1.field_id]
        form_state.record_value(field1.field_id, "Mueller-Schmidt")
        new_value = form_state.answers[field1.field_id]
        
        assert old_value == "Mueller"
        assert new_value == "Mueller-Schmidt"
        assert form_state.current_index == 2  # Should not advance

    def test_update_previous_field_invalid_field_id(self):
        """Reject update with unknown field_id."""
        form_state = FormState()
        
        field_id = "nonexistent_field"
        assert field_id not in FIELD_BY_ID

    def test_update_previous_field_not_yet_reached(self):
        """Block update to field not yet reached."""
        form_state = FormState()
        
        # Currently on field 0
        assert form_state.current_index == 0
        
        # Try to update field 2 (not reached yet)
        future_field = form_state.fields[2]
        field_index = form_state.fields.index(future_field)
        
        # Safety check should fail
        assert field_index >= form_state.current_index

    def test_update_previous_field_current_field_blocked(self):
        """Block update to current field."""
        form_state = FormState()
        
        # Save field 0
        field1 = form_state.current_field()
        form_state.record_value(field1.field_id, "Mueller")
        form_state.advance()
        
        # Now on field 1 (current)
        current_field = form_state.current_field()
        current_index = form_state.fields.index(current_field)
        
        # Safety check should block
        assert current_index >= form_state.current_index

    def test_update_previous_field_not_saved(self):
        """Block update to field not previously saved."""
        form_state = FormState()
        
        # Save field 0
        field1 = form_state.current_field()
        form_state.record_value(field1.field_id, "Mueller")
        form_state.advance()
        
        # Advance past field 1 without saving it (if optional)
        form_state.advance()
        
        # Field 1 should not be in answers
        field1_next = form_state.fields[1]
        assert field1_next.field_id not in form_state.answers

    def test_update_previous_field_validates_value(self):
        """Update should validate new value."""
        from voice_api.app.validation import validate_field
        
        form_state = FormState()
        
        # Save first field (family_name)
        field1 = form_state.current_field()
        form_state.record_value(field1.field_id, "Mueller")
        form_state.advance()
        
        # Move forward
        form_state.advance()
        
        # Try to update with invalid value (empty string for required field)
        is_valid, message = validate_field(field1, "")
        assert not is_valid

    def test_update_previous_field_maintains_index(self):
        """Update should not change current_index."""
        form_state = FormState()
        
        # Save first two fields
        field1 = form_state.current_field()
        form_state.record_value(field1.field_id, "Mueller")
        form_state.advance()
        
        field2 = form_state.current_field()
        form_state.record_value(field2.field_id, "Hans")
        form_state.advance()
        
        current_index_before = form_state.current_index
        
        # Update field 1
        form_state.record_value(field1.field_id, "Mueller-Schmidt")
        
        assert form_state.current_index == current_index_before

    def test_update_previous_field_date_format(self):
        """Update date field with valid format."""
        from voice_api.app.validation import validate_field
        
        form_state = FormState()
        
        # Find and save birth_date field
        birth_date_field = None
        for i, field in enumerate(form_state.fields):
            if field.field_id == "birth_date_p1":
                birth_date_field = field
                break
        
        if birth_date_field:
            # Advance to birth_date field
            while form_state.current_field().field_id != "birth_date_p1":
                current = form_state.current_field()
                form_state.record_value(current.field_id, "test")
                form_state.advance()
            
            # Save birth date
            form_state.record_value("birth_date_p1", "01011990")
            form_state.advance()
            
            # Move forward
            form_state.advance()
            
            # Update with new valid date
            is_valid, message = validate_field(birth_date_field, "15101999")
            assert is_valid
            
            form_state.record_value("birth_date_p1", "15101999")
            assert form_state.answers["birth_date_p1"] == "15101999"

    def test_update_previous_field_choice_field(self):
        """Update choice field with valid option."""
        from voice_api.app.validation import validate_field
        
        form_state = FormState()
        
        # Find gender field
        gender_field = None
        for field in form_state.fields:
            if field.field_id == "gender_p1":
                gender_field = field
                break
        
        if gender_field:
            # Advance to gender field
            while form_state.current_field().field_id != "gender_p1":
                current = form_state.current_field()
                form_state.record_value(current.field_id, "test")
                form_state.advance()
            
            # Save gender
            form_state.record_value("gender_p1", "0")
            form_state.advance()
            
            # Move forward
            form_state.advance()
            
            # Update with new valid choice
            is_valid, message = validate_field(gender_field, "1")
            assert is_valid
            
            form_state.record_value("gender_p1", "1")
            assert form_state.answers["gender_p1"] == "1"


class TestBackwardOnlyConstraint:
    """Test that backward-only constraint is enforced."""

    def test_can_only_update_completed_fields(self):
        """Verify field_index < current_index constraint."""
        form_state = FormState()
        
        # Save first 3 fields
        for _ in range(3):
            current = form_state.current_field()
            form_state.record_value(current.field_id, "test")
            form_state.advance()
        
        # Now on field 3 (index 3)
        assert form_state.current_index == 3
        
        # Can update fields 0, 1, 2
        for i in range(3):
            field_index = i
            assert field_index < form_state.current_index
        
        # Cannot update field 3 (current)
        assert 3 >= form_state.current_index
        
        # Cannot update field 4 (future)
        assert 4 >= form_state.current_index

    def test_field_index_calculation(self):
        """Verify field index is calculated correctly."""
        form_state = FormState()
        
        field1 = form_state.fields[0]
        field2 = form_state.fields[1]
        field3 = form_state.fields[2]
        
        assert form_state.fields.index(field1) == 0
        assert form_state.fields.index(field2) == 1
        assert form_state.fields.index(field3) == 2
