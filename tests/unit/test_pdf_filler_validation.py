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
        validate_anmeldung_data(data)
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


def test_validation_non_moving_partner_and_power_of_attorney():
    """Test validation for non-moving partner and power of attorney fields."""
    data = {
        "einzug": "15.01.25",
        "neuw.strasse": "Leopoldstraße 25 a",
        "nw.plz": "80802",
        "wohnung": 0,
        "fam1": "Müller",
        "vorn1": "Hans",
        "geschl1": 0,
        "famst1": 0,
        "gebdat1": "01.01.1990",
        "gebort1": "München",
        "staatsang1": "Deutsch",
        "rel1": 8,
        # Non-moving partner
        "fam5": "Schmidt",
        "vorn5": "Anna",
        "geschl6": 1,
        "gebdat5": "02.02.1988",
        "gebort5": "Berlin",
        # Power of attorney
        "fam_vg": "Meier",
        "vorname_vg": "Lena",
        "geb_vg": "05.05.1975",
        "fam_bev": "Koch",
        "vorname_bev": "Peter",
        "geb_bev": "10.10.1980",
        "anschrift_bev": "Bahnhofstr. 1, 80333 München",
    }
    
    try:
        validate_anmeldung_data(data)
        print("✓ Test 9 PASSED: Non-moving partner & POA validation passed")
        return True
    except ValueError as e:
        print(f"✗ Test 9 FAILED: {e}")
        return False


def test_validation_non_moving_partner_invalid_gender():
    """Test validation fails when non-moving partner gender is out of range."""
    data = {
        "einzug": "15.01.25",
        "neuw.strasse": "Leopoldstraße 25 a",
        "nw.plz": "80802",
        "wohnung": 0,
        "fam1": "Müller",
        "vorn1": "Hans",
        "geschl1": 0,
        "famst1": 0,
        "gebdat1": "01.01.1990",
        "gebort1": "München",
        "staatsang1": "Deutsch",
        "rel1": 8,
        # Non-moving partner with invalid gender value
        "fam5": "Schmidt",
        "vorn5": "Anna",
        "geschl6": 9,  # Invalid
        "gebdat5": "02.02.1988",
        "gebort5": "Berlin",
    }
    
    try:
        validate_anmeldung_data(data)
        print("✗ Test 10 FAILED: Should have rejected invalid non-moving partner gender")
        return False
    except ValueError as e:
        print(f"✓ Test 10 PASSED: Correctly rejected invalid gender: {str(e)[:100]}...")
        return True


def test_validation_optional_person_fields():
    """Test validation of optional person fields (stage name, refugee status, previous name)."""
    data = {
        "einzug": "15.01.25",
        "neuw.strasse": "Leopoldstraße 25",
        "nw.plz": "80802",
        "wohnung": 0,
        "fam1": "Mueller",
        "vorn1": "Hans",
        "geschl1": 0,
        "famst1": 0,
        "gebdat1": "05.05.1980",
        "gebort1": "Munich",
        "staatsang1": "German",
        "rel1": 0,
        # Optional person fields
        "ordenskuenstler1": "Hans the Great",  # Stage name
        "vertrieb1": "Berlin, Preussen",  # Refugee status
        "name1": "Mueller-Schmidt",  # Previous name
        # Optional fields for person 2
        "fam2": "Schmidt",
        "vorn2": "Lisa",
        "geschl2": 1,
        "famst2": 0,
        "gebdat2": "06.06.1985",
        "gebort2": "Berlin",
        "staatsang2": "German",
        "rel2": 0,
        "ordenskuenstler2": "Lisa Star",
        "vertrieb2": "Dresden, Sachsen",
        "name2": "Schmidt-Klein",
        "Ort1": "Munich",
        "Datum1": "15.01.2025"
    }
    
    try:
        validate_anmeldung_data(data)
        print("✓ Test 11 PASSED: Optional person fields validated correctly")
        return True
    except ValueError as e:
        print(f"✗ Test 11 FAILED: {str(e)[:150]}...")
        return False


def test_validation_invalid_refugee_status():
    """Test that invalid refugee status (vertrieb) is rejected."""
    data = {
        "einzug": "15.01.25",
        "neuw.strasse": "Leopoldstraße 25",
        "nw.plz": "80802",
        "wohnung": 0,
        "fam1": "Mueller",
        "vorn1": "Hans",
        "geschl1": 0,
        "famst1": 0,
        "gebdat1": "05.05.1980",
        "gebort1": "Munich",
        "staatsang1": "German",
        "rel1": 0,
        "vertrieb1": "",  # Invalid: cannot be empty string
        "Ort1": "Munich",
        "Datum1": "15.01.2025"
    }
    
    try:
        validate_anmeldung_data(data)
        print("✗ Test 12 FAILED: Should have rejected invalid refugee status")
        return False
    except ValueError as e:
        print(f"✓ Test 12 PASSED: Correctly rejected invalid refugee status: {str(e)[:100]}...")
        return True


def test_validation_legal_representative():
    """Test validation of legal representative field (gesetzlver)."""
    data = {
        "einzug": "15.01.25",
        "neuw.strasse": "Leopoldstraße 25",
        "nw.plz": "80802",
        "wohnung": 0,
        "fam1": "Mueller",
        "vorn1": "Hans",
        "geschl1": 0,
        "famst1": 0,
        "gebdat1": "05.05.1980",
        "gebort1": "Munich",
        "staatsang1": "German",
        "rel1": 0,
        "gesetzlver": "Dr. Schmidt & Partner GmbH",
        "Ort1": "Munich",
        "Datum1": "15.01.2025"
    }
    
    try:
        validate_anmeldung_data(data)
        print("✓ Test 13 PASSED: Legal representative field validated correctly")
        return True
    except ValueError as e:
        print(f"✗ Test 13 FAILED: {str(e)[:150]}...")
        return False


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
        test_validation_non_moving_partner_and_power_of_attorney,
        test_validation_non_moving_partner_invalid_gender,
        test_validation_optional_person_fields,
        test_validation_invalid_refugee_status,
        test_validation_legal_representative,
    ]
    
    results = [test() for test in tests]
    
    print("\n" + "="*70)
    print(f"RESULTS: {sum(results)}/{len(results)} tests passed")
    print("="*70 + "\n")
    
    return all(results)


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
