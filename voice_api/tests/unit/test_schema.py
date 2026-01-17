"""Unit tests for field definitions."""

from voice_api.core import ANMELDUNG_FORM_FIELDS, FIELD_BY_ID, FIELD_BY_PDF_ID


class TestAnmeldungFields:
    """Tests for field definitions."""

    def test_all_fields_defined(self):
        """All required fields should be defined."""
        assert len(ANMELDUNG_FORM_FIELDS) == 11

    def test_field_by_id_lookup(self):
        """Fields should be accessible by field_id."""
        field = FIELD_BY_ID.get("family_name_p1")
        assert field is not None
        assert field.label == "Family name"

    def test_field_by_pdf_id_lookup(self):
        """Fields should be accessible by pdf_field_id."""
        field = FIELD_BY_PDF_ID.get("fam1")
        assert field is not None
        assert field.field_id == "family_name_p1"

    def test_unique_field_ids(self):
        """All field_ids should be unique."""
        ids = [f.field_id for f in ANMELDUNG_FORM_FIELDS]
        assert len(ids) == len(set(ids))

    def test_unique_pdf_field_ids(self):
        """All pdf_field_ids should be unique."""
        pdf_ids = [f.pdf_field_id for f in ANMELDUNG_FORM_FIELDS]
        assert len(pdf_ids) == len(set(pdf_ids))

    def test_all_fields_have_validator(self):
        """All fields should have a validator."""
        for field in ANMELDUNG_FORM_FIELDS:
            assert field.validator is not None
            assert field.validator.type in [
                "text",
                "date_de",
                "integer_choice",
                "postal_code_de",
            ]

    def test_choice_fields_have_enum_values(self):
        """Choice fields should have enum_values."""
        choice_fields = [
            f
            for f in ANMELDUNG_FORM_FIELDS
            if f.validator.type == "integer_choice"
        ]
        for field in choice_fields:
            assert field.enum_values is not None
            assert len(field.enum_values) > 0

    def test_field_validator_config(self):
        """Integer choice fields should have min/max config."""
        gender_field = FIELD_BY_ID["gender_p1"]
        assert gender_field.validator.config is not None
        assert "min" in gender_field.validator.config
        assert "max" in gender_field.validator.config

    def test_all_fields_have_examples(self):
        """All fields should have at least one example."""
        for field in ANMELDUNG_FORM_FIELDS:
            assert field.examples is not None
            assert len(field.examples) > 0
