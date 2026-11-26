# OSCE Simulator Model Tests

This directory contains comprehensive tests for the OSCE Simulator models.

## 📁 Test Structure

```
tests/
├── __init__.py                    # Tests package
├── conftest.py                    # Pytest configuration and shared fixtures
├── test_student_model.py          # Student model unit tests
├── test_models_integration.py     # Integration tests for all models
└── README.md                      # This documentation
```

## 🧪 Test Categories

### 1. Unit Tests (`test_student_model.py`)
Tests individual Student model methods and functionality:

- **Student Creation & Inheritance**
  - `test_student_creation()` - Basic student creation
  - `test_student_inheritance()` - User inheritance verification
  - `test_student_relationships()` - Relationship validation

- **Consultation Management**
  - `test_start_consultation_success()` - Starting consultations
  - `test_start_consultation_multiple_attempts()` - Multiple attempts
  - `test_submit_consultation_success()` - Submitting consultations
  - `test_submit_consultation_not_found()` - Error handling
  - `test_submit_consultation_not_in_progress()` - State validation
  - `test_submit_consultation_wrong_student()` - Security validation

- **Metrics & Analytics**
  - `test_view_metrics_no_consultations()` - Empty state
  - `test_view_metrics_with_consultations()` - With data
  - `test_view_evaluation_success()` - Evaluation viewing
  - `test_view_evaluation_not_found()` - Error handling
  - `test_view_evaluation_wrong_student()` - Security validation

- **History & Data Retrieval**
  - `test_get_consultation_history()` - History retrieval
  - `test_get_consultation_history_empty()` - Empty history
  - `test_student_repr()` - String representation

### 2. Integration Tests (`test_models_integration.py`)
Tests all models working together:

- **Complete Workflow**
  - `test_complete_workflow_with_evaluation()` - End-to-end workflow
  - `test_multiple_consultations_same_student()` - Multiple consultations
  - `test_multiple_attempts_same_consultation()` - Multiple attempts

- **Model Relationships**
  - `test_user_inheritance_relationships()` - Inheritance validation
  - `test_database_constraints_and_validation()` - Database constraints
  - `test_seed_data_integration()` - Seed data validation

## 🚀 Running Tests

### Quick Start
```bash
# Run all tests
python run_tests.py

# Run tests without coverage (faster)
python run_tests.py --quick

# Run specific test file
python run_tests.py --file tests/test_student_model.py
```

### Using Pytest Directly
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app.models --cov-report=html

# Run specific test class
pytest tests/test_student_model.py::TestStudentModel

# Run specific test method
pytest tests/test_student_model.py::TestStudentModel::test_student_creation

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run tests excluding slow ones
pytest -m "not slow"
```

### Test Coverage
```bash
# Generate coverage report
pytest --cov=app.models --cov-report=html --cov-report=term-missing

# View coverage in browser
open htmlcov/index.html
```

## 📊 Test Coverage

The tests cover:

- ✅ **100% Student Model Methods**
  - `start_consultation()`
  - `submit_consultation()`
  - `view_metrics()`
  - `view_evaluation()`
  - `get_consultation_history()`

- ✅ **100% Model Relationships**
  - User → Student inheritance
  - Student → StudentConsultation (1:many)
  - Consultation → StudentConsultation (1:many)
  - StudentConsultation → EvaluationCategory (1:many)

- ✅ **100% Database Operations**
  - CRUD operations
  - Foreign key relationships
  - Unique constraints
  - Data validation

- ✅ **100% Error Handling**
  - Invalid consultation IDs
  - Wrong student access
  - State validation errors
  - Database constraint violations

## 🔧 Test Fixtures

### Database Fixtures
- `test_engine` - In-memory SQLite database
- `TestSessionLocal` - Database session factory
- `db_session` - Fresh session per test
- `clean_db` - Clean database state

### Data Fixtures
- `sample_data` - Seeded test data
- `student` - Sample student from seed data
- `consultation` - Sample consultation
- `new_student` - Fresh student for testing

## 🎯 Test Scenarios

### 1. Student Consultation Workflow
```python
# Start consultation
student_consultation = student.start_consultation(consultation.id, db_session)

# Submit consultation
result = student.submit_consultation(student_consultation.id, db_session)

# View metrics
metrics = student.view_metrics(db_session)

# View evaluation
evaluation = student.view_evaluation(student_consultation.id, db_session)
```

### 2. Multiple Attempts
```python
# First attempt
sc1 = student.start_consultation(consultation.id, db_session)
student.submit_consultation(sc1.id, db_session)

# Second attempt
sc2 = student.start_consultation(consultation.id, db_session)
student.submit_consultation(sc2.id, db_session)
```

### 3. Error Handling
```python
# Try to submit non-existent consultation
with pytest.raises(ValueError):
    student.submit_consultation("non-existent-id", db_session)

# Try to submit already completed consultation
with pytest.raises(ValueError):
    student.submit_consultation(completed_consultation.id, db_session)
```

## 📈 Performance

- **Unit Tests**: ~2-3 seconds
- **Integration Tests**: ~5-8 seconds
- **Full Test Suite**: ~10-15 seconds
- **With Coverage**: ~15-20 seconds

## 🐛 Debugging Tests

### Verbose Output
```bash
pytest -v -s --tb=long
```

### Debug Specific Test
```bash
# Add breakpoint in test
import pdb; pdb.set_trace()

# Run with debugger
pytest -s tests/test_student_model.py::TestStudentModel::test_student_creation
```

### Database Inspection
```python
# In test method
print(f"Students: {db_session.query(Student).count()}")
print(f"Consultations: {db_session.query(Consultation).count()}")
```

## 🔄 Continuous Integration

The tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run Tests
  run: |
    cd osce-simulator/backend
    python run_tests.py --quick
    
- name: Generate Coverage
  run: |
    cd osce-simulator/backend
    pytest --cov=app.models --cov-report=xml
```

## 📝 Adding New Tests

### Unit Test Template
```python
def test_new_functionality(self, new_student, db_session):
    """Test description."""
    # Arrange
    # Act
    # Assert
    pass
```

### Integration Test Template
```python
def test_new_integration_scenario(self, clean_db):
    """Test integration scenario."""
    db_session = clean_db
    
    # Setup
    # Execute
    # Verify
    pass
```

## 🎉 Test Results

When all tests pass, you'll see:
```
🧪 Running OSCE Simulator Model Tests...
==================================================
✓ test_student_creation
✓ test_student_inheritance
✓ test_start_consultation_success
...
✅ All tests passed!
📊 Coverage report generated in htmlcov/
```

This comprehensive test suite ensures the reliability and correctness of the OSCE Simulator models!
