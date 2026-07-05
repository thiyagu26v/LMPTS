# Architecture

## Layered Architecture

LMPTS follows strict layered architecture with unidirectional dependencies:

```mermaid
graph TB
    subgraph Presentation
        GUI[Tkinter GUI]
        CTRL[Controllers]
    end
    subgraph Service
        CS[CourseService]
        LS[LearnerService]
        ES[EnrollmentService]
        LPS[LearningPathService]
        AS[AnalyticsService]
    end
    subgraph Repository
        CR[CourseRepository]
        LR[LearnerRepository]
        ER[EnrollmentRepository]
        PR[PrerequisiteRepository]
    end
    subgraph Database
        DB[(SQLite)]
    end
    subgraph Domain
        MODELS[Models]
        ALGO[Algorithms]
        PAT[Patterns]
        EXC[Exceptions]
    end

    GUI --> CTRL
    CTRL --> CS & LS & ES & LPS & AS
    CS & LS & ES & LPS & AS --> CR & LR & ER & PR
    CS & ES & LPS & AS --> ALGO
    CR & LR & ER & PR --> DB
    CS & LS & ES --> MODELS
    CS & LS & ES --> PAT
    MODELS --> EXC
```

## Dependency Rules

1. **Domain Layer** never depends on GUI, services, or database
2. **Service Layer** never contains SQL
3. **Repository Layer** hides database implementation
4. **GUI** communicates only through controllers → services

## Module Responsibilities

| Module | Responsibility |
|--------|----------------|
| `core/models.py` | Domain entities with OOP encapsulation |
| `core/algorithms.py` | Graph algorithms (independent of persistence) |
| `core/patterns.py` | Design pattern implementations |
| `core/exceptions.py` | Domain exception hierarchy |
| `data/database.py` | Connection management (Singleton) |
| `data/repository.py` | CRUD abstractions (Repository Pattern) |
| `services/*.py` | Business rule orchestration |
| `gui/*.py` | User interface (MVC) |

## Sequence: Enrollment Flow

```mermaid
sequenceDiagram
    participant U as Learner (GUI)
    participant C as LearnerController
    participant ES as EnrollmentService
    participant G as PrerequisiteGraph
    participant ER as EnrollmentRepository

    U->>C: Enroll(learner_id, course_code)
    C->>ES: enroll(learner_id, course_code)
    ES->>ES: Validate learner exists
    ES->>ES: Validate course published
    ES->>G: get_transitive_prerequisites(course)
    ES->>ER: list_completed_by_learner(learner)
    ES->>ES: Check missing prerequisites
    alt Prerequisites met
        ES->>ER: create(enrollment)
        ES->>ES: notify_observers()
        ES-->>C: Enrollment
        C-->>U: Success
    else Missing prerequisites
        ES-->>C: PrerequisiteNotMetError
        C-->>U: Error message
    end
```

## ER Diagram

```mermaid
erDiagram
    COURSES ||--o{ PREREQUISITES : "prerequisite_code"
    COURSES ||--o{ PREREQUISITES : "dependent_code"
    COURSES ||--o{ ENROLLMENTS : "course_code"
    LEARNERS ||--o{ ENROLLMENTS : "learner_id"

    COURSES {
        text code PK
        text name
        text difficulty
        real duration_hours
        text status
    }
    LEARNERS {
        text learner_id PK
        text name
        text email UK
    }
    PREREQUISITES {
        int id PK
        text prerequisite_code FK
        text dependent_code FK
    }
    ENROLLMENTS {
        int id PK
        text learner_id FK
        text course_code FK
        text status
        real score
    }
```
