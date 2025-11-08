# JobGlove Backend Test Suite

## Overview

Comprehensive test suite for the JobGlove backend, covering:
- Database models and operations
- LaTeX generation (escaping, bolding, file naming)
- AI services (scoring, review)
- API endpoints
- Integration workflows

## Running Tests

### Quick Test (No dependencies)
For a fast check of core functionality without external dependencies:

```bash
python tests/simple_test.py
```

This runs a simplified test suite that covers:
- LaTeX escaping and bolding
- Database operations
- Filename generation

### Full Test Suite (with pytest)

Install test dependencies first:
```bash
pip install -r requirements.txt
```

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=. --cov-report=html
```

Run specific test categories:
```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Specific test file
pytest tests/test_database.py

# Specific test class
pytest tests/test_database.py::TestDatabaseModels

# Specific test
pytest tests/test_database.py::TestDatabaseModels::test_create_resume
```

Run verbose output:
```bash
pytest -v
```

Run with output (see print statements):
```bash
pytest -s
```

## Test Structure

```
tests/
├── __init__.py                  # Test package init
├── conftest.py                  # Shared fixtures and test helpers
├── test_database.py             # Database model tests
├── test_latex_generator.py      # LaTeX generation tests
├── test_scoring_service.py      # Resume scoring tests
├── test_review_service.py       # Resume review tests
├── test_routes.py               # API endpoint tests
├── simple_test.py               # Quick standalone test script
└── README.md                    # This file
```

## Test Coverage

### Database Tests (test_database.py)
- Creating resume records
- Resume-version relationships
- Resume-score relationships
- Resume-review bullet relationships
- Cascade deletes
- Serialization (to_dict methods)

### LaTeX Generator Tests (test_latex_generator.py)
- Character escaping ($, %, &, _, {, }, etc.)
- Metric bolding (percentages, currency, numbers, years)
- Bold + escape integration
- Filename generation with user info
- Filename sanitization
- UUID fallback for missing user info

### Scoring Service Tests (test_scoring_service.py)
- Successful scoring with all 5 categories
- JSON parsing from AI responses
- Markdown fence handling
- Total score calculation
- Error handling and fallbacks
- Service factory creation

### Review Service Tests (test_review_service.py)
- Bullet-by-bullet analysis
- Section identification
- Fallback extraction
- Relevance scoring
- Error handling
- Empty resume handling

### API Route Tests (test_routes.py)
- /api/check-apis endpoint
- /api/score endpoint
- /api/review endpoint
- /api/resumes/history endpoint
- /api/resumes/search endpoint
- /api/tailor-resume with new fields
- Database integration
- Error responses

## Fixtures

Common test fixtures available in `conftest.py`:
- `app` - Flask application for testing
- `client` - Test client for API requests
- `db_session` - In-memory database session
- `sample_resume_text` - Example resume text
- `sample_job_description` - Example job posting
- `mock_openai_response` - Mocked AI API response
- `mock_scoring_response` - Mocked scoring data
- `mock_review_response` - Mocked review data

## Writing New Tests

### Unit Test Example
```python
import pytest

@pytest.mark.unit
def test_my_function():
    result = my_function()
    assert result == expected_value
```

### Integration Test Example
```python
import pytest

@pytest.mark.integration
def test_api_endpoint(client):
    response = client.post('/api/endpoint', json={'key': 'value'})
    assert response.status_code == 200
```

### Using Fixtures
```python
def test_with_fixtures(client, sample_resume_text):
    response = client.post('/api/score', json={
        'resume_text': sample_resume_text,
        'job_description': 'Test job',
        'api': 'openai'
    })
    assert response.status_code == 200
```

## Test Markers

- `@pytest.mark.unit` - Unit tests (fast, isolated)
- `@pytest.mark.integration` - Integration tests (slower, multiple components)
- `@pytest.mark.slow` - Tests that take longer to run

Run tests by marker:
```bash
pytest -m unit        # Only unit tests
pytest -m integration # Only integration tests
pytest -m "not slow"  # Skip slow tests
```

## CI/CD Integration

For automated testing in CI/CD pipelines:

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests with coverage
pytest --cov=. --cov-report=xml --cov-report=term

# Check coverage threshold (example: 80%)
pytest --cov=. --cov-fail-under=80
```

## Troubleshooting

### Import Errors
Ensure the backend directory is in your Python path:
```bash
export PYTHONPATH="${PYTHONPATH}:/path/to/JobGlove/backend"
```

### Database Errors
Tests use an in-memory SQLite database. If you see database errors, ensure:
- SQLAlchemy is installed
- Database models are properly imported

### Mock Errors
If mocks aren't working:
- Check that pytest-mock is installed
- Verify mock paths match actual import paths
- Use `patch` with the correct module path

## Contributing

When adding new features:
1. Write tests first (TDD approach)
2. Ensure all tests pass before submitting
3. Maintain test coverage above 80%
4. Update this README if adding new test categories
