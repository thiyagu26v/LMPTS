# Domain Model

## Entity Hierarchy

```
Identifiable (ABC)
└── TimestampedEntity (ABC)
    ├── Course
    ├── Learner
    └── Enrollment

PrerequisiteRelation (frozen dataclass - value object)
PathStatistics (dataclass)
LearnerProgress (dataclass)
```

## Enums

- `DifficultyLevel`: beginner, intermediate, advanced, expert
- `CourseStatus`: draft, published, archived
- `EnrollmentStatus`: enrolled, in_progress, completed, dropped

## Relationships

- Course M:N Course (via prerequisites)
- Learner 1:N Enrollment
- Course 1:N Enrollment

## Validation Rules

- Course code: non-empty, uppercase
- Duration: > 0
- Score: 0-100 or null
- Email: must contain @
- No self-prerequisites
