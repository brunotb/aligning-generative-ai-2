"""
Unit tests for PDF filler validation functions.
Tests both validation and PDF filling functionality.
"""

import sys
import os

# Add the parent directory (project root) to the path to import api module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from api.pdf_filler import validate_anmeldung_data


def test_validation_with_valid_data():
    """Test validation passes with correct data."""
    data = {
        # Move details
        "einzug": "15.01.25",
        "neuw.strasse": "Leopoldstraße 25 a, 3. Stock",
        "nw.plz": "80802",
        "wohnung": 0,
        
        # Person 1 data
        "fam1": "von Gräfenberg",
        "vorn1": "Maria-Luisa",
        "gr1": "Dr.",
        "geschl1": 1,  # Female
        "famst1": 0,   # Single
        "gebdat1": "01.01.1990",
        "gebort1": "São Paulo, Brasilien",
        "staatsang1": "Deutsch, Brasilianisch",
        "rel1": 0,     # Roman Catholic
        
        # Signature
        "Ort1": "München",
        "Datum1": "15.01.2025"
    }
    
    try:
        validated = validate_anmeldung_data(data)
        print("✓ Test 1 PASSED: Valid data accepted")
        return True
    except ValueError as e:
        print(f"✗ Test 1 FAILED: {e}")
        return False


def test_validation_missing_required_field():
    """Test validation fails with missing required field."""
    data = {
        "einzug": "15.01.25",
        "neuw.strasse": "Leopoldstraße 25 a",
        "nw.plz": "80802",
        "wohnung": 0,
        "fam1": "von Gräfenberg",
        "vorn1": "Maria-Luisa",
        # Missing: geschl1, famst1, gebdat1, gebort1, staatsang1, rel1
    }
    
    try:
        validate_anmeldung_data(data)
        print("✗ Test 2 FAILED: Should have raised ValueError for missing fields")
        return False
    except ValueError as e:
        print(f"✓ Test 2 PASSED: Correctly rejected missing field: {str(e)[:80]}...")
        return True


def test_validation_invalid_date_format():
    """Test validation fails with invalid date format."""
    data = {
        "einzug": "2025-01-15",  # Wrong format (should be DD.MM.YY)
        "neuw.strasse": "Leopoldstraße 25 a",
        "nw.plz": "80802",
        "wohnung": 0,
        "fam1": "von Gräfenberg",
        "vorn1": "Maria-Luisa",
        "geschl1": 1,
        "famst1": 0,
        "gebdat1": "01.01.1990",
        "gebort1": "São Paulo",
        "staatsang1": "Deutsch",
        "rel1": 0,
    }
    
    try:
        validate_anmeldung_data(data)
        print("✗ Test 3 FAILED: Should have raised ValueError for invalid date format")
        return False
    except ValueError as e:
        print(f"✓ Test 3 PASSED: Correctly rejected invalid date: {str(e)[:80]}...")
        return True


def test_validation_invalid_gender_range():
    """Test validation fails with invalid gender value."""
    data = {
        "einzug": "15.01.25",
        "neuw.strasse": "Leopoldstraße 25 a",
        "nw.plz": "80802",
        "wohnung": 0,
        "fam1": "von Gräfenberg",
        "vorn1": "Maria-Luisa",
        "geschl1": 5,  # Invalid: should be 0-3
        "famst1": 0,
        "gebdat1": "01.01.1990",
        "gebort1": "São Paulo",
        "staatsang1": "Deutsch",
        "rel1": 0,
    }
    
    try:
        validate_anmeldung_data(data)
        print("✗ Test 4 FAILED: Should have raised ValueError for invalid gender")
        return False
    except ValueError as e:
        print(f"✓ Test 4 PASSED: Correctly rejected invalid gender: {str(e)[:80]}...")
        return True


def test_validation_invalid_housing_type():
    """Test validation fails with invalid housing type."""
    data = {
        "einzug": "15.01.25",
        "neuw.strasse": "Leopoldstraße 25 a",
        "nw.plz": "80802",
        "wohnung": 5,  # Invalid: should be 0-2
        "fam1": "von Gräfenberg",
        "vorn1": "Maria-Luisa",
        "geschl1": 1,
        "famst1": 0,
        "gebdat1": "01.01.1990",
        "gebort1": "São Paulo",
        "staatsang1": "Deutsch",
        "rel1": 0,
    }
    
    try:
        validate_anmeldung_data(data)
        print("✗ Test 5 FAILED: Should have raised ValueError for invalid housing type")
        return False
    except ValueError as e:
        print(f"✓ Test 5 PASSED: Correctly rejected invalid housing type: {str(e)[:80]}...")
        return True


def test_validation_married_without_date():
    """Test validation fails when married but no marriage date provided."""
    data = {
        "einzug": "15.01.25",
        "neuw.strasse": "Leopoldstraße 25 a",
        "nw.plz": "80802",
        "wohnung": 0,
        "fam1": "von Gräfenberg",
        "vorn1": "Maria-Luisa",
        "geschl1": 1,
        "famst1": 1,  # Married (VH)
        # Missing: dat1
        "gebdat1": "01.01.1990",
        "gebort1": "São Paulo",
        "staatsang1": "Deutsch",
        "rel1": 0,
    }
    
    try:
        validate_anmeldung_data(data)
        print("✗ Test 6 FAILED: Should require marriage date for married status")
        return False
    except ValueError as e:
        print(f"✓ Test 6 PASSED: Correctly required marriage date: {str(e)[:80]}...")
        return True


def test_validation_multiple_persons():
    """Test validation with multiple persons."""
    data = {
        "einzug": "15.01.25",
        "neuw.strasse": "Leopoldstraße 25 a",
        "nw.plz": "80802",
        "wohnung": 1,  # Hauptwohnung
        
        # Person 1
        "fam1": "Müller",
        "vorn1": "Hans",
        "geschl1": 0,  # Male
        "famst1": 1,   # Married
        "gebdat1": "10.05.1985",
        "gebort1": "München",
        "staatsang1": "Deutsch",
        "rel1": 8,     # Evangelisch
        "dat1": "10.08.2015, Rom",
        
        # Person 2 (Spouse)
        "fam2": "Müller",
        "vorn2": "Anna",
        "geschl2": 1,  # Female
        "famst2": 1,   # Married
        "gebdat2": "20.03.1987",
        "gebort2": "Berlin",
        "staatsang2": "Deutsch",
        "rel2": 8,     # Evangelisch
        "dat2": "10.08.2015, Rom",
        
        # Person 3 (Child)
        "fam3": "Müller",
        "vorn3": "Alex",
        "geschl3": 3,  # Diverse
        "famst3": 0,   # Single
        "gebdat3": "01.01.2015",
        "gebort3": "München",
        "staatsang3": "Deutsch",
        "rel3": 21,    # oa (Ohne Angabe)
        
        "Ort1": "München",
        "Datum1": "15.01.2025"
    }
    
    try:
        validated = validate_anmeldung_data(data)
        print("✓ Test 7 PASSED: Multiple persons validation passed")
        return True
    except ValueError as e:
        print(f"✗ Test 7 FAILED: {str(e)[:120]}...")
        return False


def test_validation_mismatched_marriage_dates():
    """Test validation fails when spouses have different marriage dates."""
    data = {
        "einzug": "15.01.25",
        "neuw.strasse": "Leopoldstraße 25 a",
        "nw.plz": "80802",
        "wohnung": 1,
        
        "fam1": "Müller",
        "vorn1": "Hans",
        "geschl1": 0,
        "famst1": 1,  # Married
        "gebdat1": "10.05.1985",
        "gebort1": "München",
        "staatsang1": "Deutsch",
        "rel1": 8,
        "dat1": "10.08.2015, Rom",  # Date 1
        
        "fam2": "Schmidt",
        "vorn2": "Anna",
        "geschl2": 1,
        "famst2": 1,  # Married
        "gebdat2": "20.03.1987",
        "gebort2": "Berlin",
        "staatsang2": "Deutsch",
        "rel2": 8,
        "dat2": "10.08.2016, Berlin",  # Different date!
    }
    
    try:
        validate_anmeldung_data(data)
        print("✗ Test 8 FAILED: Should detect mismatched marriage dates")
        return False
    except ValueError as e:
        print(f"✓ Test 8 PASSED: Correctly detected mismatched dates: {str(e)[:80]}...")
        return True


def run_all_tests():
    """Run all tests and report results."""
    print("\n" + "="*70)
    print("RUNNING PDF FILLER VALIDATION TESTS")
    print("="*70 + "\n")
    
    tests = [
        test_validation_with_valid_data,
        test_validation_missing_required_field,
        test_validation_invalid_date_format,
        test_validation_invalid_gender_range,
        test_validation_invalid_housing_type,
        test_validation_married_without_date,
        test_validation_multiple_persons,
        test_validation_mismatched_marriage_dates,
    ]
    
    results = [test() for test in tests]
    
    print("\n" + "="*70)
    print(f"RESULTS: {sum(results)}/{len(results)} tests passed")
    print("="*70 + "\n")
    
    return all(results)


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
