# Test Report

**Date:** July 5, 2026  
**Project:** LMPTS Capstone  
**Author:** Suganthan S

## Summary

| Metric | Result |
|--------|--------|
| Total Tests | 95 |
| Passed | 95 |
| Failed | 0 |
| Skipped | 0 |
| Coverage | 83.88% |
| Duration | ~5.4 seconds |

## Coverage by Module

| Module | Coverage |
|--------|----------|
| core/algorithms.py | ~95% |
| core/models.py | ~90% |
| core/patterns.py | ~88% |
| core/exceptions.py | 100% |
| core/enums.py | ~95% |
| data/database.py | ~85% |
| data/repository.py | ~82% |
| services/course_service.py | ~85% |
| services/enrollment_service.py | ~88% |
| services/learning_path_service.py | ~90% |
| services/analytics_service.py | ~85% |
| services/learner_service.py | ~65% |
| gui/* | 0% (manual testing) |

## Test Categories

### Unit Tests (58)
- Model validation and encapsulation
- Graph algorithms (BFS, DFS, cycle detection)
- Design patterns (Factory, Strategy, Observer)
- Repository CRUD operations

### Integration Tests (12)
- Full enrollment workflow
- Course/prerequisite management workflow
- Learning path computation workflow
- Analytics after enrollment changes

### Edge Case Tests (14)
- Empty inputs, invalid scores, archived courses
- Duplicate enrollments and prerequisites
- Large graph performance (100 nodes)
- Transaction rollback

### Service Tests (11)
- All FR1-FR6 service methods
- Error handling for each domain exception

## Edge Cases Validated

- Empty course code
- Self-prerequisite
- Circular dependency (A→B→C→A)
- Enrollment without prerequisites
- Duplicate enrollment
- Archived course enrollment
- Invalid difficulty level
- Zero/negative duration
- Score out of range (0-100)
- Nonexistent learner/course
- Empty learning path
- Path with duplicate courses

## Performance Metrics

- 100-node chain shortest path: < 1ms
- Full test suite: ~5.4 seconds
- Database initialization with seed: < 100ms

## Known Limitations

- GUI layer not covered by automated tests (Tkinter requires display)
- `logging_config.py` not unit tested
- Deprecation warnings for `datetime.utcnow()` (non-blocking)

## HTML Coverage Report

Generated at: `docs/reports/coverage_html/index.html`

Regenerate with:
```bash
python -m pytest tests/ --cov=lmpts --cov-report=html:docs/reports/coverage_html
```
