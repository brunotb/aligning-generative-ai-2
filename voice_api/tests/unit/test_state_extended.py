"""Extended unit tests for voice_api.app.state module."""

import pytest
from voice_api.app import FormState
from voice_api.core import ANMELDUNG_FORM_FIELDS


class TestFormStateBasics:
    """Test FormState basic functionality."""

    def test_form_state_initialization(self):
        """FormState should initialize with correct defaults."""
        form_state = FormState()
        
        assert form_state.current_index == 0
        assert len(form_state.answers) == 0
        assert len(form_state.validation_errors) == 0
        assert len(form_state.fields) > 0

    def test_current_field_at_start(self):
        """current_field returns first field at start."""
        form_state = FormState()
        field = form_state.current_field()
        
        assert field is not None
        assert field == form_state.fields[0]

    def test_advance_increments_index(self):
        """advance() increments current_index."""
        form_state = FormState()
        initial_index = form_state.current_index
        
        form_state.advance()
        
        assert form_state.current_index == initial_index + 1

    def test_current_field_progression(self):
        """current_field changes as we advance."""
        form_state = FormState()
        field1 = form_state.current_field()
        
        form_state.advance()
        field2 = form_state.current_field()
        
        assert field1 != field2

    def test_current_field_at_end(self):
        """current_field returns None when at end."""
        form_state = FormState()
        
        num_fields = len(form_state.fields)
        for _ in range(num_fields + 1):
            form_state.advance()
        
        assert form_state.current_field() is None


class TestRecordValue:
    """Test record_value method."""

    def test_record_value_stores_answer(self):
        """record_value stores the value in answers dict."""
        form_state = FormState()
        
        form_state.record_value("test_field", "test_value")
        
        assert "test_field" in form_state.answers
        assert form_state.answers["test_field"] == "test_value"

    def test_record_value_clears_error(self):
        """record_value removes error for that field."""
        form_state = FormState()
        
        # Set an error
        form_state.set_error("test_field", "Test error")
        assert "test_field" in form_state.validation_errors
        
        # Record a value clears the error
        form_state.record_value("test_field", "test_value")
        
        assert "test_field" not in form_state.validation_errors

    def test_record_multiple_values(self):
        """Can record values for multiple fields."""
        form_state = FormState()
        
        form_state.record_value("field1", "value1")
        form_state.record_value("field2", "value2")
        form_state.record_value("field3", "value3")
        
        assert len(form_state.answers) == 3
        assert form_state.answers["field1"] == "value1"
        assert form_state.answers["field2"] == "value2"
        assert form_state.answers["field3"] == "value3"

    def test_record_value_overwrites(self):
        """Recording a new value overwrites the old one."""
        form_state = FormState()
        
        form_state.record_value("field", "old_value")
        form_state.record_value("field", "new_value")
        
        assert form_state.answers["field"] == "new_value"


class TestSetError:
    """Test set_error method."""

    def test_set_error_stores_error(self):
        """set_error stores error in validation_errors."""
        form_state = FormState()
        
        form_state.set_error("field", "Error message")
        
        assert "field" in form_state.validation_errors
        assert form_state.validation_errors["field"] == "Error message"

    def test_set_error_overwrites(self):
        """Setting a new error overwrites the old one."""
        form_state = FormState()
        
        form_state.set_error("field", "Error 1")
        form_state.set_error("field", "Error 2")
        
        assert form_state.validation_errors["field"] == "Error 2"

    def test_multiple_field_errors(self):
        """Can track errors for multiple fields."""
        form_state = FormState()
        
        form_state.set_error("field1", "Error 1")
        form_state.set_error("field2", "Error 2")
        
        assert len(form_state.validation_errors) == 2


class TestProgressTracking:
    """Test progress_percent method."""

    def test_progress_initially_zero(self):
        """Progress is 0% with no answers."""
        form_state = FormState()
        assert form_state.progress_percent() == 0.0

    def test_progress_increases_with_answers(self):
        """Progress increases as answers are recorded."""
        form_state = FormState()
        initial = form_state.progress_percent()
        
        field = form_state.current_field()
        form_state.record_value(field.field_id, "answer")
        
        new_progress = form_state.progress_percent()
        assert new_progress > initial

    def test_progress_reaches_100(self):
        """Progress reaches 100% when all fields answered."""
        form_state = FormState()
        
        for field in form_state.fields:
            form_state.record_value(field.field_id, "answer")
        
        assert form_state.progress_percent() == 100.0

    def test_progress_bounded_at_100(self):
        """Progress never exceeds 100%."""
        form_state = FormState()
        
        # Record answers for all fields
        for field in form_state.fields:
            form_state.record_value(field.field_id, "answer")
        
        # Record extra answers
        form_state.record_value("extra_field", "extra_value")
        
        progress = form_state.progress_percent()
        assert progress <= 100.0

    def test_progress_is_percentage(self):
        """Progress is between 0 and 100."""
        form_state = FormState()
        
        # No answers
        assert 0 <= form_state.progress_percent() <= 100
        
        # Some answers
        field1 = form_state.current_field()
        form_state.record_value(field1.field_id, "answer")
        assert 0 <= form_state.progress_percent() <= 100
        
        # All answers
        for field in form_state.fields:
            form_state.record_value(field.field_id, "answer")
        assert 0 <= form_state.progress_percent() <= 100


class TestIsComplete:
    """Test is_complete method."""

    def test_is_complete_false_at_start(self):
        """is_complete is False initially."""
        form_state = FormState()
        assert not form_state.is_complete()

    def test_is_complete_true_after_advancing_past_end(self):
        """is_complete is True after advancing past last field."""
        form_state = FormState()
        
        num_fields = len(form_state.fields)
        for _ in range(num_fields):
            form_state.advance()
        
        assert form_state.is_complete()

    def test_is_complete_false_on_last_field(self):
        """is_complete is False on the last field."""
        form_state = FormState()
        
        num_fields = len(form_state.fields)
        for _ in range(num_fields - 1):
            form_state.advance()
        
        assert not form_state.is_complete()


class TestToPDFFormat:
    """Test to_pdf_format conversion."""

    def test_to_pdf_format_returns_dict(self):
        """to_pdf_format returns a dictionary."""
        form_state = FormState()
        pdf_format = form_state.to_pdf_format()
        
        assert isinstance(pdf_format, dict)

    def test_to_pdf_format_empty_when_no_answers(self):
        """to_pdf_format returns empty dict with no answers."""
        form_state = FormState()
        pdf_format = form_state.to_pdf_format()
        
        assert len(pdf_format) == 0

    def test_to_pdf_format_with_answers(self):
        """to_pdf_format converts recorded answers."""
        form_state = FormState()
        
        form_state.record_value("family_name_p1", "Mueller")
        pdf_format = form_state.to_pdf_format()
        
        # Should have converted to PDF format
        assert isinstance(pdf_format, dict)
        # Should contain some mapping of the answer
        assert len(pdf_format) > 0


class TestFormStateEdgeCases:
    """Test edge cases."""

    def test_advance_past_end(self):
        """Can safely advance past the end of form."""
        form_state = FormState()
        
        num_fields = len(form_state.fields)
        for _ in range(num_fields + 10):
            form_state.advance()
        
        # Should remain complete
        assert form_state.is_complete()

    def test_empty_string_answer(self):
        """Can record empty string as answer."""
        form_state = FormState()
        
        form_state.record_value("field", "")
        
        assert "field" in form_state.answers
        assert form_state.answers["field"] == ""

    def test_special_characters_in_value(self):
        """Can record special characters."""
        form_state = FormState()
        
        special_value = "Müller-Döring, Jr. (2024)"
        form_state.record_value("field", special_value)
        
        assert form_state.answers["field"] == special_value

    def test_long_value(self):
        """Can record long values."""
        form_state = FormState()
        
        long_value = "A" * 10000
        form_state.record_value("field", long_value)
        
        assert form_state.answers["field"] == long_value


class TestErrorHandling:
    """Test error handling workflow."""

    def test_set_and_clear_error_via_record_value(self):
        """Recording a value clears the error."""
        form_state = FormState()
        field_id = "test_field"
        
        # Set error
        form_state.set_error(field_id, "Invalid")
        assert field_id in form_state.validation_errors
        
        # Record value (clears error)
        form_state.record_value(field_id, "Valid")
        assert field_id not in form_state.validation_errors

    def test_multiple_errors_independent(self):
        """Errors for different fields are independent."""
        form_state = FormState()
        
        form_state.set_error("field1", "Error 1")
        form_state.set_error("field2", "Error 2")
        
        # Clearing one doesn't affect the other
        form_state.record_value("field1", "value1")
        
        assert "field1" not in form_state.validation_errors
        assert "field2" in form_state.validation_errors

    def test_error_message_preserved(self):
        """Error message is preserved correctly."""
        form_state = FormState()
        
        error_msg = "This is a detailed error message"
        form_state.set_error("field", error_msg)
        
        assert form_state.validation_errors["field"] == error_msg


class TestFormCompletion:
    """Test complete form workflows."""

    def test_full_form_progression(self):
        """Progressing through entire form."""
        form_state = FormState()
        
        initial_count = len(form_state.fields)
        
        # Collect answers for all fields
        for i, field in enumerate(form_state.fields):
            assert form_state.current_field() == field
            form_state.record_value(field.field_id, f"Answer {i}")
            form_state.advance()
        
        # Should be complete now
        assert form_state.is_complete()
        assert len(form_state.answers) == initial_count
        assert form_state.progress_percent() == 100.0

    def test_form_with_errors(self):
        """Form progression with error handling."""
        form_state = FormState()
        
        field = form_state.current_field()
        
        # First attempt with error
        form_state.set_error(field.field_id, "Invalid format")
        
        # Correct the error
        form_state.record_value(field.field_id, "ValidValue")
        form_state.advance()
        
        # Progress continued
        assert field.field_id in form_state.answers
        assert form_state.current_field() != field


class TestFieldAccess:
    """Test field access patterns."""

    def test_all_fields_accessible(self):
        """All form fields are accessible."""
        form_state = FormState()
        
        assert len(form_state.fields) == len(ANMELDUNG_FORM_FIELDS)
        for i, expected_field in enumerate(ANMELDUNG_FORM_FIELDS):
            assert form_state.fields[i] == expected_field

    def test_field_properties_preserved(self):
        """Field properties are preserved in state."""
        form_state = FormState()
        
        for state_field in form_state.fields:
            # Field should have basic properties
            assert hasattr(state_field, "field_id")
            assert hasattr(state_field, "label")
            assert hasattr(state_field, "description")
            assert len(state_field.field_id) > 0
            assert len(state_field.label) > 0
