# Database Design

## Overview

LMPTS uses **SQLite** with a normalized schema, foreign keys, indexes, and cascade deletes.

## Schema

### courses
| Column | Type | Constraints |
|--------|------|-------------|
| code | TEXT | PRIMARY KEY |
| name | TEXT | NOT NULL |
| description | TEXT | DEFAULT '' |
| difficulty | TEXT | CHECK (beginner/intermediate/advanced/expert) |
| duration_hours | REAL | CHECK (> 0) |
| instructor | TEXT | DEFAULT '' |
| status | TEXT | CHECK (draft/published/archived) |

### learners
| Column | Type | Constraints |
|--------|------|-------------|
| learner_id | TEXT | PRIMARY KEY |
| name | TEXT | NOT NULL |
| email | TEXT | NOT NULL UNIQUE |

### prerequisites
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| prerequisite_code | TEXT | FK → courses(code) ON DELETE CASCADE |
| dependent_code | TEXT | FK → courses(code) ON DELETE CASCADE |
| | | UNIQUE(prerequisite_code, dependent_code) |
| | | CHECK (prerequisite_code != dependent_code) |

### enrollments
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| learner_id | TEXT | FK → learners(learner_id) ON DELETE CASCADE |
| course_code | TEXT | FK → courses(code) ON DELETE CASCADE |
| status | TEXT | CHECK (enrolled/in_progress/completed/dropped) |
| score | REAL | CHECK (0-100 or NULL) |
| | | UNIQUE(learner_id, course_code) |

## Indexes

- `idx_prerequisites_dependent` — fast prerequisite lookup by course
- `idx_prerequisites_prereq` — fast dependent lookup
- `idx_enrollments_learner` — learner enrollment history
- `idx_enrollments_course` — course enrollment stats
- `idx_enrollments_status` — completion filtering
- `idx_courses_status` — published course catalog

## Migration

File: `lmpts/data/migrations/001_initial_schema.sql`

Run automatically on `DatabaseManager.initialize()`.

## Seed Data

8 sample courses forming prerequisite chains:
- CS101 → CS102 → CS201 → CS301
- MATH101 → MATH201, CS201
- CS101 → WEB101 → DB201

3 learners with sample enrollments.

## Repository Abstraction

Services never execute SQL directly. All access through:
- `CourseRepository`
- `LearnerRepository`
- `EnrollmentRepository`
- `PrerequisiteRepository`

## Transaction Support

```python
with db.transaction() as conn:
    conn.execute("INSERT ...")
    conn.execute("UPDATE ...")
# Auto-commit or rollback on error
```
