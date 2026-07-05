# Edge Cases

| Case | Handling | Test |
|------|----------|------|
| Empty course code | ValidationError | test_models |
| Self-prerequisite | EntityValidationError | test_models |
| Circular dependency | CircularDependencyError | test_algorithms |
| Duplicate enrollment | EnrollmentError | test_services |
| Missing prerequisites | PrerequisiteNotMetError | test_integration |
| Archived course enrollment | EnrollmentError | test_edge_cases |
| Invalid score (>100) | EntityValidationError | test_models |
| Zero duration | EntityValidationError | test_edge_cases |
| Nonexistent course | CourseNotFoundError | test_edge_cases |
| Empty learning path | validate_path returns False | test_edge_cases |
| Duplicate path courses | validate_path returns False | test_edge_cases |
| Transaction failure | Rollback, DatabaseError | test_database |
| 100-node graph | Performance test passes | test_edge_cases |
