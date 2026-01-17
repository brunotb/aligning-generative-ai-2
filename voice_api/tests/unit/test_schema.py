"""Unit tests for schema and field definitions."""

from voice_api import anmeldung_fields, schema


class TestAnmeldungFields:
    """Tests for anmeldung_fields module."""

    def test_all_fields_defined(self):
        """All required fields should be defined."""
        assert len(anmeldung_fields.ANMELDUNG_FORM_FIELDS) == 13

    def test_field_by_id_lookup(self):
        """Fields should be accessible by field_id."""
        field = anmeldung_fields.FIELD_BY_ID.get("family_name_p1")
        assert field is not None
        assert field.label == "Family name"

    def test_field_by_pdf_id_lookup(self):
        """Fields should be accessible by pdf_field_id."""
        field = anmeldung_fields.FIELD_BY_PDF_ID.get("fam1")
        assert field is not None
        assert field.field_id == "family_name_p1"

    def test_unique_field_ids(self):
        """All field_ids should be unique."""
        ids = [f.field_id for f in anmeldung_fields.ANMELDUNG_FORM_FIELDS]
        assert len(ids) == len(set(ids))

    def test_unique_pdf_field_ids(self):
        """All pdf_field_ids should be unique."""
        pdf_ids = [f.pdf_field_id for f in anmeldung_fields.ANMELDUNG_FORM_FIELDS]
        assert len(pdf_ids) == len(set(pdf_ids))

    def test_all_fields_have_validator(self):
        """All fields should have a validator."""
        for field in anmeldung_fields.ANMELDUNG_FORM_FIELDS:
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
            for f in anmeldung_fields.ANMELDUNG_FORM_FIELDS
            if f.validator.type == "integer_choice"
        ]
        for field in choice_fields:
            assert field.enum_values is not None
            assert len(field.enum_values) > 0

    def test_field_validator_config(self):
        """Integer choice fields should have min/max config."""
        gender_field = anmeldung_fields.FIELD_BY_ID["gender_p1"]
        assert gender_field.validator.config is not None
        assert "min" in gender_field.validator.config
        assert "max" in gender_field.validator.config

    def test_all_fields_have_examples(self):
        """All fields should have at least one example."""
        for field in anmeldung_fields.ANMELDUNG_FORM_FIELDS:
            assert field.examples is not None
            assert len(field.examples) > 0


class TestSchemaConversion:
    """Tests for schema module field conversions."""

    def test_form_fields_count(self):
        """FormFields should match AnmeldungFields count."""
        assert len(schema.FORM_FIELDS) == len(
            anmeldung_fields.ANMELDUNG_FORM_FIELDS
        )

    def test_form_field_properties(self):
        """FormFields should have all required properties."""
        for form_field in schema.FORM_FIELDS:
            assert form_field.field_id is not None
            assert form_field.label is not None
            assert form_field.description is not None
            assert form_field.field_type is not None
            assert form_field.pdf_field_id is not None
            assert form_field.validator_type is not None
            assert form_field.validator_config is not None

    def test_field_type_consistency(self):
        """field_type should match validator_type."""
        for form_field in schema.FORM_FIELDS:
            assert form_field.field_type == form_field.validator_type

    def test_enum_values_preserved(self):
        """Enum values should be preserved in conversion."""
        gender_form_field = [
            f for f in schema.FORM_FIELDS if f.field_id == "gender_p1"
        ][0]
        assert gender_form_field.enum_values is not None
        assert len(gender_form_field.enum_values) == 4

    def test_examples_preserved(self):
        """Examples should be preserved in conversion."""
        family_name_field = [
            f for f in schema.FORM_FIELDS if f.field_id == "family_name_p1"
        ][0]
        assert family_name_field.examples is not None
        assert "Mueller" in family_name_field.examples
