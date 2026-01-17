"""Integration tests for form workflow."""

from voice_api import schema, validation, state, pdf_generator


class TestValidationWorkflow:
    """Test validation of different field types."""

    def test_validate_text_field(self):
        """Text fields should validate correctly."""
        family_name_field = [
            f for f in schema.FORM_FIELDS if f.field_id == "family_name_p1"
        ][0]
        
        # Valid
        is_valid, msg = validation.validate_field(family_name_field, "Mueller")
        assert is_valid is True
        
        # Empty
        is_valid, msg = validation.validate_field(family_name_field, "")
        assert is_valid is False

    def test_validate_date_field(self):
        """Date fields should validate in DD.MM.YYYY format."""
        birth_date_field = [
            f for f in schema.FORM_FIELDS if f.field_id == "birth_date_p1"
        ][0]
        
        # Valid
        is_valid, msg = validation.validate_field(birth_date_field, "15.01.1990")
        assert is_valid is True
        
        # Invalid format
        is_valid, msg = validation.validate_field(birth_date_field, "1990-01-15")
        assert is_valid is False
        
        # Invalid day
        is_valid, msg = validation.validate_field(birth_date_field, "32.01.1990")
        assert is_valid is False

    def test_validate_integer_choice_field(self):
        """Choice fields should validate integer ranges."""
        gender_field = [
            f for f in schema.FORM_FIELDS if f.field_id == "gender_p1"
        ][0]
        
        # Valid
        is_valid, msg = validation.validate_field(gender_field, "0")
        assert is_valid is True
        
        is_valid, msg = validation.validate_field(gender_field, "3")
        assert is_valid is True
        
        # Out of range
        is_valid, msg = validation.validate_field(gender_field, "5")
        assert is_valid is False

    def test_validate_postal_code_field(self):
        """Postal code fields should validate German postal codes."""
        postal_field = [
            f for f in schema.FORM_FIELDS if f.field_id == "new_postal_code"
        ][0]
        
        # Valid 5-digit
        is_valid, msg = validation.validate_field(postal_field, "80802")
        assert is_valid is True
        
        # Invalid length
        is_valid, msg = validation.validate_field(postal_field, "808")
        assert is_valid is False


class TestFormState:
    """Test FormState tracking and progression."""

    def test_initial_state(self):
        """Form should start at first field."""
        form = state.FormState()
        assert form.current_index == 0
        assert form.current_field() is not None
        assert form.is_complete() is False

    def test_record_and_advance(self):
        """Recording a value should advance to next field."""
        form = state.FormState()
        first_field = form.current_field()
        
        form.record_value(first_field.field_id, "Mueller")
        assert form.answers[first_field.field_id] == "Mueller"
        assert form.validation_errors == {}
        
        form.advance()
        assert form.current_index == 1

    def test_set_and_clear_error(self):
        """Setting an error and then recording a value should clear it."""
        form = state.FormState()
        first_field = form.current_field()
        
        form.set_error(first_field.field_id, "Invalid value")
        assert first_field.field_id in form.validation_errors
        
        form.record_value(first_field.field_id, "Mueller")
        assert first_field.field_id not in form.validation_errors

    def test_progress_percent(self):
        """Progress should increase as fields are filled."""
        form = state.FormState()
        assert form.progress_percent() == 0.0
        
        first_field = form.current_field()
        form.record_value(first_field.field_id, "Mueller")
        
        initial_progress = form.progress_percent()
        assert initial_progress > 0.0

    def test_form_completion(self):
        """Form should be complete when all fields are filled."""
        form = state.FormState()
        
        # Fill all fields
        while not form.is_complete():
            field = form.current_field()
            if field:
                # Use first example or default value
                value = field.examples[0] if field.examples else "test"
                form.record_value(field.field_id, value)
            form.advance()
        
        assert form.is_complete() is True
        assert form.progress_percent() == 100.0


class TestPdfFormatTransformation:
    """Test conversion of form answers to PDF format."""

    def test_transform_text_fields(self):
        """Text fields should pass through as-is."""
        answers = {
            "family_name_p1": "Mueller",
            "first_name_p1": "Max",
            "birth_place_p1": "Berlin"
        }
        
        pdf_data = pdf_generator.transform_answers_to_pdf_format(answers)
        
        assert pdf_data["fam1"] == "Mueller"
        assert pdf_data["vorn1"] == "Max"
        assert pdf_data["gebort1"] == "Berlin"

    def test_transform_integer_choice_fields(self):
        """Integer choice fields should convert string to int."""
        answers = {
            "gender_p1": "1",
            "family_status_p1": "0",
            "housing_type": "2"
        }
        
        pdf_data = pdf_generator.transform_answers_to_pdf_format(answers)
        
        assert pdf_data["geschl1"] == 1
        assert isinstance(pdf_data["geschl1"], int)
        assert pdf_data["famst1"] == 0
        assert isinstance(pdf_data["famst1"], int)
        assert pdf_data["wohnung"] == 2

    def test_transform_date_fields(self):
        """Date fields should pass through in DD.MM.YYYY format."""
        answers = {
            "birth_date_p1": "15.01.1990",
            "move_in_date": "01.02.2025"
        }
        
        pdf_data = pdf_generator.transform_answers_to_pdf_format(answers)
        
        assert pdf_data["gebdat1"] == "15.01.1990"
        assert pdf_data["einzug"] == "01.02.2025"

    def test_transform_unknown_field_skipped(self):
        """Unknown fields should be silently skipped."""
        answers = {
            "family_name_p1": "Mueller",
            "unknown_field": "should be ignored"
        }
        
        pdf_data = pdf_generator.transform_answers_to_pdf_format(answers)
        
        assert "fam1" in pdf_data
        assert len(pdf_data) == 1  # Only known field

    def test_full_form_transformation(self):
        """Complete form should transform to valid PDF format."""
        answers = {
            "family_name_p1": "Mueller",
            "first_name_p1": "Max",
            "birth_date_p1": "15.01.1990",
            "birth_place_p1": "Berlin",
            "gender_p1": "0",
            "family_status_p1": "0",
            "nationality_p1": "German",
            "religion_p1": "8",
            "move_in_date": "01.02.2025",
            "new_street_address": "Leopoldstraße 25a",
            "new_postal_code": "80802",
            "new_city": "München",
            "housing_type": "1"
        }
        
        pdf_data = pdf_generator.transform_answers_to_pdf_format(answers)
        
        # Check all PDF field IDs are present
        assert pdf_data["fam1"] == "Mueller"
        assert pdf_data["vorn1"] == "Max"
        assert pdf_data["gebdat1"] == "15.01.1990"
        assert pdf_data["gebort1"] == "Berlin"
        assert pdf_data["geschl1"] == 0
        assert pdf_data["famst1"] == 0
        assert pdf_data["staatsang1"] == "German"
        assert pdf_data["rel1"] == 8
        assert pdf_data["einzug"] == "01.02.2025"
        assert pdf_data["neuw.strasse"] == "Leopoldstraße 25a"
        assert pdf_data["nw.plz"] == "80802"
        assert pdf_data["nw.ort"] == "München"
        assert pdf_data["wohnung"] == 1


class TestEnumDisplay:
    """Test human-readable enum value display."""

    def test_get_enum_display_gender(self):
        """Gender field should display enum labels."""
        gender_field = [
            f for f in schema.FORM_FIELDS if f.field_id == "gender_p1"
        ][0]
        
        assert "Male" in validation.get_enum_display(gender_field, "0")
        assert "Female" in validation.get_enum_display(gender_field, "1")
        assert "Diverse" in validation.get_enum_display(gender_field, "3")

    def test_get_enum_display_unknown_value(self):
        """Unknown enum value should return original value."""
        gender_field = [
            f for f in schema.FORM_FIELDS if f.field_id == "gender_p1"
        ][0]
        
        result = validation.get_enum_display(gender_field, "999")
        assert result == "999"

    def test_get_enum_display_non_choice_field(self):
        """Non-choice fields should return value as-is."""
        name_field = [
            f for f in schema.FORM_FIELDS if f.field_id == "family_name_p1"
        ][0]
        
        result = validation.get_enum_display(name_field, "Mueller")
        assert result == "Mueller"
