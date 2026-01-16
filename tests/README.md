# Test Suite

This directory contains all tests for the Anmeldung PDF Filler application.

## Structure

```
tests/
├── __init__.py              # Test package marker
├── conftest.py              # Pytest configuration and shared fixtures
├── unit/                    # Unit tests
│   ├── __init__.py
│   └── test_pdf_filler_validation.py
├── integration/             # Integration tests
│   ├── __init__.py
│   └── test_pdf_filling.py
└── README.md               # This file
```

## Running Tests

### Run all tests

```bash
pytest tests/
```

### Run specific test file

```bash
pytest tests/unit/test_pdf_filler_validation.py
```

### Run tests with verbose output

```bash
pytest tests/ -v
```

### Run tests with coverage report

```bash
pytest tests/ --cov=api --cov-report=html
```

### Run only unit tests

```bash
pytest tests/unit -m unit
```

### Run only integration tests

```bash
pytest tests/integration -m integration
```

## Test Categories

Tests are organized by type:

- **Unit Tests** (`tests/unit/`): Test individual functions and modules in isolation
  - File: `test_pdf_filler_validation.py`
  - Validates input data without creating actual PDFs
  - Tests all validation rules and error handling

- **Integration Tests** (`tests/integration/`): Test interactions between modules and actual PDF creation
  - File: `test_pdf_filling.py`
  - Creates actual PDF files using the template
  - Reads PDFs back to verify they are correctly filled
  - Tests complete workflows with real data

## CI/CD Integration

The test suite is automatically run via GitHub Actions on:

- Every push to `main` or `develop` branches
- Every pull request to `main` or `develop` branches

See `.github/workflows/ci.yml` for the CI/CD configuration.

## Writing Tests

When adding new tests:

1. Place unit tests in `tests/unit/`
2. Name test files as `test_*.py`
3. Name test functions as `test_*`
4. Use descriptive test names that explain what is being tested
5. Add docstrings to test functions
6. Use appropriate pytest markers for categorization

Example test structure:

```python
def test_some_feature():
    """Test that feature X works as expected."""
    # Arrange
    input_data = {...}
    
    # Act
    result = function_under_test(input_data)
    
    # Assert
    assert result == expected_output
```

## Dependencies

Test dependencies are listed in `api/requirements.txt`:

- pytest: Test framework
- pytest-cov: Coverage reporting plugin

Install with:

```bash
pip install -r api/requirements.txt
```
