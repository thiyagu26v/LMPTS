# Error Handling

## Exception Hierarchy

```
LMPTSError
├── ValidationError
│   └── EntityValidationError
├── CourseNotFoundError
├── LearnerNotFoundError
├── CircularDependencyError
├── EnrollmentError
│   └── PrerequisiteNotMetError
├── RepositoryError
│   └── DatabaseError
└── ServiceError
```

## Usage Pattern

Services raise domain exceptions; controllers/GUI catch and display messages:

```python
try:
    service.enroll(learner_id, course_code)
except PrerequisiteNotMetError as e:
    show_error(e.message)
```

## Validation Layers

1. **Model validation** — `entity.validate()` at creation
2. **Factory validation** — raises `EntityValidationError`
3. **Service validation** — business rules (prerequisites, duplicates)
4. **Database constraints** — CHECK, UNIQUE, FOREIGN KEY
5. **GUI validation** — input format checks before service calls
