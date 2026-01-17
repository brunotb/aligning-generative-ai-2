"""Tests for voice_api.core.fields module."""

import pytest
from voice_api.core.fields import (
    AnmeldungField,
    ANMELDUNG_FORM_FIELDS,
    FIELD_BY_ID,
    FIELD_BY_PDF_ID,
)


class TestAnmeldungFieldsStructure:
    """Test the structure of anmeldung fields."""

    def test_anmeldung_form_fields_not_empty(self):
        """ANMELDUNG_FORM_FIELDS should contain fields."""
        assert len(ANMELDUNG_FORM_FIELDS) > 0
        assert len(ANMELDUNG_FORM_FIELDS) >= 10

    def test_all_fields_are_anmeldung_fields(self):
        """All items in list should be AnmeldungField instances."""
        for field in ANMELDUNG_FORM_FIELDS:
            assert isinstance(field, AnmeldungField)

    def test_field_id_uniqueness(self):
        """Each field should have unique field_id."""
        field_ids = [f.field_id for f in ANMELDUNG_FORM_FIELDS]
        assert len(field_ids) == len(set(field_ids))

    def test_pdf_field_id_uniqueness(self):
        """Each field should have unique pdf_field_id."""
        pdf_ids = [f.pdf_field_id for f in ANMELDUNG_FORM_FIELDS]
        assert len(pdf_ids) == len(set(pdf_ids))


class TestAnmeldungFieldProperties:
    """Test properties of individual fields."""

    def test_field_has_required_attributes(self):
        """Each field should have all required attributes."""
        for field in ANMELDUNG_FORM_FIELDS:
            assert hasattr(field, "field_id")
            assert hasattr(field, "pdf_field_id")
            assert hasattr(field, "label")
            assert hasattr(field, "description")
            assert hasattr(field, "validator")
            assert hasattr(field, "required")

    def test_field_id_is_nonempty_string(self):
        """field_id should be non-empty string."""
        for field in ANMELDUNG_FORM_FIELDS:
            assert isinstance(field.field_id, str)
            assert len(field.field_id) > 0

    def test_pdf_field_id_is_nonempty_string(self):
        """pdf_field_id should be non-empty string."""
        for field in ANMELDUNG_FORM_FIELDS:
            assert isinstance(field.pdf_field_id, str)
            assert len(field.pdf_field_id) > 0

    def test_label_is_nonempty_string(self):
        """label should be non-empty string."""
        for field in ANMELDUNG_FORM_FIELDS:
            assert isinstance(field.label, str)
            assert len(field.label) > 0

    def test_description_is_nonempty_string(self):
        """description should be non-empty string."""
        for field in ANMELDUNG_FORM_FIELDS:
            assert isinstance(field.description, str)
            assert len(field.description) > 0

    def test_validator_exists(self):
        """validator should not be None."""
        for field in ANMELDUNG_FORM_FIELDS:
            assert field.validator is not None


class TestLookupMaps:
    """Test the lookup dictionaries."""

    def test_field_by_id_contains_all_fields(self):
        """FIELD_BY_ID should contain all field_ids."""
        assert len(FIELD_BY_ID) == len(ANMELDUNG_FORM_FIELDS)

    def test_field_by_id_maps_correctly(self):
        """FIELD_BY_ID should map field_id to field."""
        for field in ANMELDUNG_FORM_FIELDS:
            assert FIELD_BY_ID[field.field_id] == field

    def test_field_by_pdf_id_contains_all_fields(self):
        """FIELD_BY_PDF_ID should contain all pdf_field_ids."""
        assert len(FIELD_BY_PDF_ID) == len(ANMELDUNG_FORM_FIELDS)

    def test_field_by_pdf_id_maps_correctly(self):
        """FIELD_BY_PDF_ID should map pdf_field_id to field."""
        for field in ANMELDUNG_FORM_FIELDS:
            assert FIELD_BY_PDF_ID[field.pdf_field_id] == field

    def test_lookup_retrieval(self):
        """Can retrieve fields by both ids."""
        if ANMELDUNG_FORM_FIELDS:
            test_field = ANMELDUNG_FORM_FIELDS[0]
            
            # Lookup by field_id
            found_by_field_id = FIELD_BY_ID.get(test_field.field_id)
            assert found_by_field_id == test_field
            
            # Lookup by pdf_field_id
            found_by_pdf_id = FIELD_BY_PDF_ID.get(test_field.pdf_field_id)
            assert found_by_pdf_id == test_field


class TestFieldValidators:
    """Test field validators."""

    def test_all_fields_have_validator_type(self):
        """All fields should have validator type defined."""
        valid_types = ["text", "date_de", "integer_choice", "postal_code_de"]
        
        for field in ANMELDUNG_FORM_FIELDS:
            assert field.validator.type in valid_types

    def test_choice_fields_have_enum_values(self):
        """Choice fields should have enum_values."""
        for field in ANMELDUNG_FORM_FIELDS:
            if field.validator.type == "integer_choice":
                assert field.enum_values is not None
                assert len(field.enum_values) > 0

    def test_choice_fields_have_min_max(self):
        """Choice fields should have min/max in validator."""
        for field in ANMELDUNG_FORM_FIELDS:
            if field.validator.type == "integer_choice":
                assert "min" in field.validator.config or "min_val" in field.validator.config
                assert "max" in field.validator.config or "max_val" in field.validator.config


class TestFieldExamples:
    """Test field examples."""

    def test_fields_may_have_examples(self):
        """Fields may optionally have examples."""
        has_examples = 0
        for field in ANMELDUNG_FORM_FIELDS:
            if field.examples:
                has_examples += 1
                assert isinstance(field.examples, list)
                if field.examples:
                    assert isinstance(field.examples[0], str)
        
        # At least some fields should have examples
        assert has_examples > 0

    def test_examples_are_strings(self):
        """Examples should be strings."""
        for field in ANMELDUNG_FORM_FIELDS:
            if field.examples:
                for example in field.examples:
                    assert isinstance(example, str)


class TestFieldConstraints:
    """Test field constraints."""

    def test_required_field_attribute(self):
        """required should be boolean."""
        for field in ANMELDUNG_FORM_FIELDS:
            assert isinstance(field.required, bool)

    def test_most_fields_are_required(self):
        """Most personal info fields should be required."""
        required_count = sum(1 for f in ANMELDUNG_FORM_FIELDS if f.required)
        total_count = len(ANMELDUNG_FORM_FIELDS)
        
        # At least 70% should be required
        assert required_count / total_count >= 0.7


class TestFieldConsistency:
    """Test consistency across fields."""

    def test_no_empty_labels(self):
        """No field should have empty label."""
        for field in ANMELDUNG_FORM_FIELDS:
            assert len(field.label) > 0

    def test_no_empty_descriptions(self):
        """No field should have empty description."""
        for field in ANMELDUNG_FORM_FIELDS:
            assert len(field.description) > 0

    def test_field_ids_follow_pattern(self):
        """Field IDs should follow naming patterns."""
        for field in ANMELDUNG_FORM_FIELDS:
            # Should be lowercase or have underscore
            assert field.field_id.islower() or "_" in field.field_id

    def test_pdf_field_ids_follow_pattern(self):
        """PDF field IDs should follow expected patterns."""
        for field in ANMELDUNG_FORM_FIELDS:
            # PDF IDs usually start with abbreviations
            assert len(field.pdf_field_id) >= 2


class TestFieldCategorization:
    """Test field categorization."""

    def test_personal_fields_exist(self):
        """Should have fields for personal info."""
        personal_keywords = ["name", "first", "birth", "gender"]
        personal_field_ids = [f.field_id for f in ANMELDUNG_FORM_FIELDS]
        
        found_personal = any(
            any(keyword in fid for keyword in personal_keywords)
            for fid in personal_field_ids
        )
        assert found_personal

    def test_address_fields_exist(self):
        """Should have fields for address."""
        address_keywords = ["street", "postal", "city", "address", "house"]
        address_field_ids = [f.field_id for f in ANMELDUNG_FORM_FIELDS]
        
        found_address = any(
            any(keyword in fid for keyword in address_keywords)
            for fid in address_field_ids
        )
        assert found_address


class TestFieldSerializability:
    """Test that fields can be serialized."""

    def test_field_to_dict_like_structure(self):
        """Fields should be accessible as dict-like via dataclass."""
        for field in ANMELDUNG_FORM_FIELDS:
            # Should be able to access as attributes
            _ = field.field_id
            _ = field.label
            _ = field.description
            _ = field.validator
            _ = field.required


class TestAnmeldungFieldDefaults:
    """Test default behaviors."""

    def test_enum_values_optional(self):
        """enum_values should be optional."""
        for field in ANMELDUNG_FORM_FIELDS:
            # Some fields may not have enum_values
            if field.validator.type != "integer_choice":
                assert field.enum_values is None or isinstance(field.enum_values, dict)

    def test_examples_optional(self):
        """examples should be optional."""
        for field in ANMELDUNG_FORM_FIELDS:
            assert field.examples is None or isinstance(field.examples, list)


class TestCompleteFormSet:
    """Test that we have a complete form set."""

    def test_minimum_field_count(self):
        """Should have at least 10 fields for complete form."""
        assert len(ANMELDUNG_FORM_FIELDS) >= 10

    def test_no_duplicate_mappings(self):
        """No duplicate field_id → pdf_field_id mappings."""
        mappings = [(f.field_id, f.pdf_field_id) for f in ANMELDUNG_FORM_FIELDS]
        assert len(mappings) == len(set(mappings))
