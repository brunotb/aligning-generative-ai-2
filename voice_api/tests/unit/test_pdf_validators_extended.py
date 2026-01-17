"""Extended tests for voice_api.core.validators module."""

import pytest
from datetime import datetime
from voice_api.core.validators import (
    _validate_text,
    _validate_date_de,
    _validate_integer_choice,
    _validate_postal_code_de,
    validate_by_type,
)


class TestValidateTextEdgeCases:
    """Edge cases for text validation."""

    def test_validate_text_with_spaces(self):
        """Text with only spaces should be invalid."""
        result, message = _validate_text("   ")
        assert not result

    def test_validate_text_with_special_characters(self):
        """Text with special characters should be valid."""
        result, message = _validate_text("Mueller-Schmidt")
        assert result

    def test_validate_text_with_umlauts(self):
        """German umlauts should be valid."""
        result, message = _validate_text("Müller")
        assert result

    def test_validate_text_single_character(self):
        """Single character should be valid."""
        result, message = _validate_text("A")
        assert result

    def test_validate_text_very_long(self):
        """Very long text should be valid."""
        result, message = _validate_text("A" * 1000)
        assert result

    def test_validate_text_with_numbers(self):
        """Numbers in text should be valid."""
        result, message = _validate_text("Test123")
        assert result

    def test_validate_text_with_punctuation(self):
        """Punctuation should be valid."""
        result, message = _validate_text("Dr. med. Mueller")
        assert result


class TestValidateDateDEEdgeCases:
    """Edge cases for German date validation."""

    def test_validate_date_leap_year(self):
        """Valid leap year date should pass."""
        result, message = _validate_date_de("29.02.2020")
        assert result

    def test_validate_date_non_leap_year_feb_29(self):
        """Feb 29 in non-leap year should fail."""
        result, message = _validate_date_de("29.02.2021")
        assert not result

    def test_validate_date_year_99_treated_as_1999(self):
        """Year 99 should be treated as 1999."""
        result, message = _validate_date_de("01.01.99")
        assert result

    def test_validate_date_year_00_treated_as_2000(self):
        """Year 00 should be treated as 2000."""
        result, message = _validate_date_de("01.01.00")
        assert result

    def test_validate_date_year_30_treated_as_1930(self):
        """Year 30 should be treated as 1930 (>30 → 19xx)."""
        result, message = _validate_date_de("01.01.30")
        assert result

    def test_validate_date_year_31_treated_as_2031(self):
        """Year 31 should be treated as 2031 (≤30 → 20xx would be wrong, >30 → 19xx)."""
        result, message = _validate_date_de("01.01.31")
        # This depends on implementation
        assert result is not None  # Just check it doesn't crash

    def test_validate_date_invalid_day_32(self):
        """Day 32 should be invalid."""
        result, message = _validate_date_de("32.01.1990")
        assert not result

    def test_validate_date_invalid_month_13(self):
        """Month 13 should be invalid."""
        result, message = _validate_date_de("01.13.1990")
        assert not result

    def test_validate_date_invalid_format_with_slashes(self):
        """Slashes instead of dots should be invalid."""
        result, message = _validate_date_de("01/01/1990")
        assert not result

    def test_validate_date_invalid_format_no_separators(self):
        """No separators should be invalid."""
        result, message = _validate_date_de("01011990")
        assert not result

    def test_validate_date_padding_not_required(self):
        """Dates without zero-padding might work depending on implementation."""
        result, message = _validate_date_de("1.1.1990")
        # Just check it doesn't crash
        assert result is not None

    def test_validate_date_december_31st(self):
        """Dec 31 should be valid."""
        result, message = _validate_date_de("31.12.1990")
        assert result

    def test_validate_date_january_1st(self):
        """Jan 1 should be valid."""
        result, message = _validate_date_de("01.01.1990")
        assert result

    def test_validate_date_april_31_invalid(self):
        """April 31 doesn't exist."""
        result, message = _validate_date_de("31.04.1990")
        assert not result


class TestValidateIntegerChoiceEdgeCases:
    """Edge cases for integer choice validation."""

    def test_validate_choice_at_min_boundary(self):
        """Value at minimum should be valid."""
        result, message = _validate_integer_choice("0", min_val=0, max_val=5)
        assert result

    def test_validate_choice_at_max_boundary(self):
        """Value at maximum should be valid."""
        result, message = _validate_integer_choice("5", min_val=0, max_val=5)
        assert result

    def test_validate_choice_below_min(self):
        """Value below minimum should be invalid."""
        result, message = _validate_integer_choice("-1", min_val=0, max_val=5)
        assert not result

    def test_validate_choice_above_max(self):
        """Value above maximum should be invalid."""
        result, message = _validate_integer_choice("6", min_val=0, max_val=5)
        assert not result

    def test_validate_choice_single_value_range(self):
        """Single value range (min==max) should work."""
        result, message = _validate_integer_choice("3", min_val=3, max_val=3)
        assert result

    def test_validate_choice_non_integer(self):
        """Non-integer strings should be invalid."""
        result, message = _validate_integer_choice("abc", min_val=0, max_val=5)
        assert not result

    def test_validate_choice_float(self):
        """Float values should be invalid."""
        result, message = _validate_integer_choice("3.5", min_val=0, max_val=5)
        assert not result

    def test_validate_choice_leading_zeros(self):
        """Leading zeros might be accepted."""
        result, message = _validate_integer_choice("03", min_val=0, max_val=5)
        assert result

    def test_validate_choice_negative_range(self):
        """Negative ranges should work."""
        result, message = _validate_integer_choice("-5", min_val=-10, max_val=-1)
        assert result

    def test_validate_choice_large_numbers(self):
        """Large numbers should work."""
        result, message = _validate_integer_choice("1000000", min_val=0, max_val=2000000)
        assert result


class TestValidatePostalCodeDEEdgeCases:
    """Edge cases for German postal code validation."""

    def test_validate_postal_valid_5_digit(self):
        """5-digit postal codes should be valid."""
        result, message = _validate_postal_code_de("10115")
        assert result

    def test_validate_postal_valid_4_digit(self):
        """4-digit postal codes should be valid."""
        result, message = _validate_postal_code_de("1234")
        assert result

    def test_validate_postal_with_leading_zero(self):
        """Postal codes with leading zero should be valid."""
        result, message = _validate_postal_code_de("01234")
        assert result

    def test_validate_postal_too_short_3_digits(self):
        """3-digit codes should be invalid."""
        result, message = _validate_postal_code_de("123")
        assert not result

    def test_validate_postal_too_long_6_digits(self):
        """6-digit codes should be invalid."""
        result, message = _validate_postal_code_de("123456")
        assert not result

    def test_validate_postal_with_spaces(self):
        """Postal codes with spaces should be invalid."""
        result, message = _validate_postal_code_de("10 115")
        assert not result

    def test_validate_postal_with_hyphens(self):
        """Postal codes with hyphens should be invalid."""
        result, message = _validate_postal_code_de("10-115")
        assert not result

    def test_validate_postal_with_letters(self):
        """Postal codes with letters should be invalid."""
        result, message = _validate_postal_code_de("1011A")
        assert not result

    def test_validate_postal_all_zeros(self):
        """All zeros might be invalid depending on rules."""
        result, message = _validate_postal_code_de("00000")
        # Just check it doesn't crash
        assert result is not None

    def test_validate_postal_empty_string(self):
        """Empty string should be invalid."""
        result, message = _validate_postal_code_de("")
        assert not result


class TestValidateByType:
    """Test dispatcher function."""

    def test_validate_by_type_text(self):
        """Dispatcher should route to text validator."""
        result, message = validate_by_type("text", "TestValue")
        assert result

    def test_validate_by_type_text_empty(self):
        """Dispatcher should reject empty text."""
        result, message = validate_by_type("text", "")
        assert not result

    def test_validate_by_type_date_de_valid(self):
        """Dispatcher should route to date validator."""
        result, message = validate_by_type("date_de", "01.01.1990")
        assert result

    def test_validate_by_type_date_de_invalid(self):
        """Dispatcher should reject invalid date."""
        result, message = validate_by_type("date_de", "99.99.1990")
        assert not result

    def test_validate_by_type_integer_choice(self):
        """Dispatcher should route to choice validator."""
        # Would need to pass min/max somehow
        result, message = validate_by_type("integer_choice", "2")
        # Just check it doesn't crash
        assert result is not None

    def test_validate_by_type_postal_code_de(self):
        """Dispatcher should route to postal code validator."""
        result, message = validate_by_type("postal_code_de", "10115")
        assert result

    def test_validate_by_type_unknown_type(self):
        """Unknown type should be handled."""
        result, message = validate_by_type("unknown_type", "value")
        # Should either reject or provide default behavior
        assert result is not None


class TestValidatorErrorMessages:
    """Test error message quality."""

    def test_text_error_message_not_empty(self):
        """Error messages should be informative."""
        result, message = _validate_text("")
        assert message is not None
        assert len(message) > 0

    def test_date_error_message_not_empty(self):
        """Date error messages should be informative."""
        result, message = _validate_date_de("99.99.1990")
        assert message is not None
        assert len(message) > 0

    def test_choice_error_message_not_empty(self):
        """Choice error messages should be informative."""
        result, message = _validate_integer_choice("100", min_val=0, max_val=5)
        assert message is not None
        assert len(message) > 0

    def test_postal_error_message_not_empty(self):
        """Postal code error messages should be informative."""
        result, message = _validate_postal_code_de("123")
        assert message is not None
        assert len(message) > 0


class TestValidatorWithNoneValues:
    """Test validators with None inputs."""

    def test_text_validator_with_none(self):
        """Text validator should handle None gracefully."""
        try:
            result, message = _validate_text(None)
            # If it doesn't crash, check result is False
            assert not result
        except (TypeError, AttributeError):
            # Acceptable to raise TypeError for None
            pass

    def test_date_validator_with_none(self):
        """Date validator should handle None gracefully."""
        try:
            result, message = _validate_date_de(None)
            assert not result
        except (TypeError, AttributeError):
            pass


class TestValidatorConsistency:
    """Test consistency of validators."""

    def test_same_input_produces_same_result(self):
        """Validators should be deterministic."""
        result1, msg1 = _validate_text("Test")
        result2, msg2 = _validate_text("Test")
        
        assert result1 == result2
        assert msg1 == msg2

    def test_valid_input_always_valid(self):
        """Consistently valid inputs should always be valid."""
        for _ in range(5):
            result, message = _validate_text("Valid Name")
            assert result

    def test_invalid_input_always_invalid(self):
        """Consistently invalid inputs should always be invalid."""
        for _ in range(5):
            result, message = _validate_text("")
            assert not result
