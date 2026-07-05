# Testing Guide

## Framework

- **pytest** — test runner
- **pytest-cov** — coverage reporting

## Test Structure

```
tests/
├── conftest.py          # Fixtures (temp DB, service container)
├── test_models.py       # Domain model unit tests
├── test_algorithms.py   # Graph algorithm tests
├── test_patterns.py     # Design pattern tests
├── test_database.py     # Database singleton tests
├── test_repositories.py # Repository CRUD tests
├── test_services.py     # Service layer tests
├── test_integration.py  # End-to-end workflows
└── test_edge_cases.py   # Edge cases and regression
```

## Running Tests

```bash
# All tests with coverage
python -m pytest tests/ -v --cov=lmpts --cov-report=term-missing

# HTML coverage report
python -m pytest tests/ --cov=lmpts --cov-report=html:docs/reports/coverage_html

# Specific test file
python -m pytest tests/test_algorithms.py -v
```

## Test Distribution

| Category | Approx % | Files |
|----------|----------|-------|
| Unit | 60% | test_models, test_algorithms, test_patterns |
| Integration | 30% | test_integration, test_services |
| Edge Cases | 10% | test_edge_cases |

## Coverage Results

- **Total:** 83.88%
- **Minimum required:** 80%
- **HTML report:** `docs/reports/coverage_html/index.html`

## Mocking Strategy

- Each test uses isolated temp SQLite database via `tmp_path` fixture
- `DatabaseManager.reset_instance()` ensures singleton isolation
- No external dependencies to mock

## Key Test Scenarios

1. Course validation (empty code, negative duration)
2. Circular dependency prevention
3. Prerequisite enrollment blocking
4. Full enrollment workflow (register → enroll → complete → next)
5. Learning path validation with transitive prerequisites
6. Transaction rollback on failure
7. 100-node graph performance
