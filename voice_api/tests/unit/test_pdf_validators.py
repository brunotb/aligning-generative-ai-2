"""Unit tests for validators module."""

import pytest

from voice_api.core import validators


class TestValidateText:
    """Tests for _validate_text validator."""

    def test_valid_text(self):
        """Non-empty text should validate."""
        is_valid, msg = validators._validate_text("Mueller")
        assert is_valid is True
        assert msg == ""

    def test_text_with_spaces(self):
        """Text with spaces should validate."""
        is_valid, msg = validators._validate_text("von Gräfenberg")
        assert is_valid is True

    def test_empty_text(self):
        """Empty text should fail."""
        is_valid, msg = validators._validate_text("")
        assert is_valid is False
        assert "empty" in msg.lower()

    def test_whitespace_only(self):
        """Whitespace-only text should fail."""
        is_valid, msg = validators._validate_text("   ")
        assert is_valid is False


class TestValidateDateDe:
    """Tests for _validate_date_de validator."""

    def test_valid_full_year(self):
        """Valid date in DDMMYYYY format should pass."""
        is_valid, msg = validators._validate_date_de("15011990")
        assert is_valid is True

    def test_valid_two_digit_year_20xx(self):
        """Two-digit year should be full 4-digit year."""
        is_valid, msg = validators._validate_date_de("15012025")
        assert is_valid is True

    def test_valid_two_digit_year_19xx(self):
        """Year in 1900s format."""
        is_valid, msg = validators._validate_date_de("15011985")
        assert is_valid is True

    def test_invalid_format_no_dots(self):
        """Date with dots should fail (requires DDMMYYYY format)."""
        is_valid, msg = validators._validate_date_de("15.01.1990")
        assert is_valid is False

    def test_invalid_day(self):
        """Invalid day (32) should fail."""
        is_valid, msg = validators._validate_date_de("32011990")
        assert is_valid is False

    def test_invalid_month(self):
        """Invalid month (13) should fail."""
        is_valid, msg = validators._validate_date_de("15131990")
        assert is_valid is False

    def test_empty_date(self):
        """Empty date should fail."""
        is_valid, msg = validators._validate_date_de("")
        assert is_valid is False


class TestValidateIntegerChoice:
    """Tests for _validate_integer_choice validator."""

    def test_valid_within_range(self):
        """Integer within range should pass."""
        is_valid, msg = validators._validate_integer_choice("1", 0, 3)
        assert is_valid is True

    def test_valid_at_min(self):
        """Integer at minimum should pass."""
        is_valid, msg = validators._validate_integer_choice("0", 0, 3)
        assert is_valid is True

    def test_valid_at_max(self):
        """Integer at maximum should pass."""
        is_valid, msg = validators._validate_integer_choice("3", 0, 3)
        assert is_valid is True

    def test_below_min(self):
        """Integer below min should fail."""
        is_valid, msg = validators._validate_integer_choice("-1", 0, 3)
        assert is_valid is False
        assert "too small" in msg.lower()

    def test_above_max(self):
        """Integer above max should fail."""
        is_valid, msg = validators._validate_integer_choice("5", 0, 3)
        assert is_valid is False
        assert "too large" in msg.lower()

    def test_non_integer(self):
        """Non-integer should fail."""
        is_valid, msg = validators._validate_integer_choice("abc", 0, 3)
        assert is_valid is False
        assert "whole number" in msg.lower()

    def test_empty_value(self):
        """Empty value should fail."""
        is_valid, msg = validators._validate_integer_choice("", 0, 3)
        assert is_valid is False

    def test_no_max_constraint(self):
        """Large integer with no max should pass."""
        is_valid, msg = validators._validate_integer_choice("999", 0, None)
        assert is_valid is True


class TestValidatePostalCodeDe:
    """Tests for _validate_postal_code_de validator."""

    def test_valid_five_digit_code(self):
        """Valid 5-digit postal code should pass."""
        is_valid, msg = validators._validate_postal_code_de("80802")
        assert is_valid is True

    def test_valid_four_digit_code(self):
        """Valid 4-digit postal code should pass."""
        is_valid, msg = validators._validate_postal_code_de("1015")
        assert is_valid is True

    def test_invalid_three_digit_code(self):
        """3-digit postal code should fail."""
        is_valid, msg = validators._validate_postal_code_de("808")
        assert is_valid is False

    def test_invalid_six_digit_code(self):
        """6-digit postal code should fail."""
        is_valid, msg = validators._validate_postal_code_de("808020")
        assert is_valid is False

    def test_non_numeric(self):
        """Non-numeric postal code should fail."""
        is_valid, msg = validators._validate_postal_code_de("8080a")
        assert is_valid is False

    def test_empty_code(self):
        """Empty postal code should fail."""
        is_valid, msg = validators._validate_postal_code_de("")
        assert is_valid is False


class TestValidateByType:
    """Tests for validate_by_type dispatch function."""

    def test_dispatch_text(self):
        """Dispatch to text validator."""
        is_valid, msg = validators.validate_by_type("text", "Mueller")
        assert is_valid is True

    def test_dispatch_date_de(self):
        """Dispatch to German date validator."""
        is_valid, msg = validators.validate_by_type("date_de", "15011990")
        assert is_valid is True

    def test_dispatch_postal_code_de(self):
        """Dispatch to German postal code validator."""
        is_valid, msg = validators.validate_by_type("postal_code_de", "80802")
        assert is_valid is True

    def test_dispatch_integer_choice(self):
        """Dispatch to integer choice validator with config."""
        is_valid, msg = validators.validate_by_type(
            "integer_choice", "2", {"min": 0, "max": 3}
        )
        assert is_valid is True

    def test_unknown_validator_type(self):
        """Unknown validator type should pass through."""
        is_valid, msg = validators.validate_by_type(
            "unknown_type", "anything"
        )
        assert is_valid is True
        assert msg == ""
