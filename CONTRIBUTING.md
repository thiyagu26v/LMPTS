# Contributing

## Development Setup

1. Fork/clone the repository
2. Create virtual environment
3. Install dev dependencies: `pip install -r requirements.txt`
4. Run tests: `python -m pytest tests/ -v`

## Code Standards

- Follow PEP 8
- Use type hints on all functions
- Format with Black: `black lmpts tests`
- Sort imports with isort: `isort lmpts tests`
- Lint with flake8: `flake8 lmpts tests`

## Architecture Rules

1. Domain layer must not import from GUI, services, or data
2. Services must not contain SQL
3. GUI must only call controllers → services
4. All new features require tests (maintain 80%+ coverage)

## Pull Request Process

1. Create feature branch
2. Write tests for new functionality
3. Update documentation
4. Ensure all tests pass
5. Submit PR with description of changes

## Adding a New Path Strategy

1. Implement `PathFindingStrategy` in `core/patterns.py`
2. Register in `LearningPathService.STRATEGIES`
3. Add unit test in `tests/test_patterns.py`

## Adding a New Repository

1. Extend `Repository[T]` ABC
2. Implement in `data/repository.py`
3. Wire in `ServiceContainer`
4. Add tests in `tests/test_repositories.py`
