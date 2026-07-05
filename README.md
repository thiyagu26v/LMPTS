# Learning Management & Prerequisite Tracking System (LMPTS)

[![Tests](https://img.shields.io/badge/tests-95%20passed-brightgreen)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-84%25-brightgreen)](docs/reports/coverage_html/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](requirements.txt)

A production-quality capstone project implementing a **Learning Management & Prerequisite Tracking System** with layered architecture, graph algorithms, design patterns, SQLite persistence, Tkinter GUI, and comprehensive test coverage.

**Author:** Suganthan S  
**Course:** C Programming Fundamentals Capstone

---

## Features

| Requirement | Implementation |
|-------------|----------------|
| FR1 Course Management | Create, update, delete, publish, archive courses |
| FR2 Prerequisite Management | Add/remove prereqs, transitive discovery, cycle detection, levels |
| FR3 Learner Management | Register learners, track progress and completion rates |
| FR4 Enrollment Validation | Prerequisite enforcement, duplicate prevention, suggestions |
| FR5 Learning Paths | BFS shortest path, multiple strategies, path statistics |
| FR6 Analytics | System metrics, completion stats, bottleneck detection |
| FR7 GUI | Admin panel, learner portal, analytics dashboard, path finder |

---

## Architecture

```
Presentation (Tkinter GUI)
        ↓
Service Layer (Business Logic)
        ↓
Repository Layer (Data Access)
        ↓
Database Layer (SQLite)
        ↓
Domain Layer (Models, Algorithms, Patterns)
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed diagrams.

---

## Folder Structure

```
sugunew/
├── lmpts/
│   ├── core/           # Domain models, algorithms, patterns, exceptions
│   ├── data/           # Database singleton, repositories, migrations
│   ├── services/       # Business logic services
│   ├── gui/            # Tkinter MVC presentation
│   └── utils/          # Logging configuration
├── tests/              # 95 automated tests (unit, integration, edge cases)
├── docs/               # Knowledge base and reports
├── main.py             # Application entry point
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## Installation

### Prerequisites
- Python 3.10 or higher
- pip

### Setup

```bash
cd sugunew
pip install -r requirements.txt
```

### Run Application

```bash
python main.py
```

### Run Tests

```bash
python -m pytest tests/ -v --cov=lmpts --cov-report=html:docs/reports/coverage_html
```

Open `docs/reports/coverage_html/index.html` for the HTML coverage report.

---

## Usage Demo

### Admin Workflow
1. Open **Admin Panel** tab
2. Create a course (Code, Name, Difficulty, Duration)
3. Click **Publish** to make it available
4. Add prerequisites (Prerequisite → Dependent)
5. System prevents circular dependencies automatically

### Learner Workflow
1. Open **Learner Portal** tab
2. Select or register a learner
3. Click **Validate** before enrolling (real-time feedback)
4. **Enroll** in available courses
5. **Mark Complete** with optional score

### Analytics
1. Open **Analytics Dashboard** tab
2. View system metrics, course completion rates, bottlenecks

### Learning Paths
1. Open **Learning Paths** tab
2. Enter start and target courses
3. Select strategy (shortest, difficulty, minimum duration)
4. View path with hours and difficulty progression

---

## Design Patterns

| Pattern | Location | Purpose |
|---------|----------|---------|
| Repository | `lmpts/data/repository.py` | Abstract data access |
| Factory | `lmpts/core/patterns.py` | Validated entity creation |
| Strategy | `lmpts/core/patterns.py` | Pluggable path-finding algorithms |
| Observer | `lmpts/core/patterns.py` | GUI refresh on enrollment events |
| Singleton | `lmpts/data/database.py` | Shared database connection |

See [DESIGN_PATTERNS.md](DESIGN_PATTERNS.md).

---

## Algorithms

| Algorithm | Complexity | Location |
|-----------|------------|----------|
| Cycle Detection (DFS) | O(V + E) | `PrerequisiteGraph.detect_cycle` |
| BFS Shortest Path | O(V + E) | `PrerequisiteGraph.shortest_path` |
| Transitive Prerequisites | O(V + E) | `PrerequisiteGraph.get_transitive_prerequisites` |
| Course Level Computation | O(V + E) | `PrerequisiteGraph.compute_course_levels` |
| Topological Sort | O(V + E) | `PrerequisiteGraph.topological_sort` |

See [ALGORITHMS.md](ALGORITHMS.md).

---

## Database

- **Engine:** SQLite with foreign keys, indexes, constraints
- **Schema:** Normalized (courses, learners, prerequisites, enrollments)
- **Migration:** `lmpts/data/migrations/001_initial_schema.sql`
- **Seed Data:** 8 courses, 3 learners, sample enrollments

See [DATABASE.md](DATABASE.md).

---

## Testing

- **95 tests** — all passing
- **83.88% coverage** (exceeds 80% requirement)
- Unit, integration, edge case, and performance tests
- See [TESTING.md](TESTING.md) and [TEST_REPORT.md](TEST_REPORT.md)

---

## Documentation Index

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | System architecture |
| [DESIGN_PATTERNS.md](DESIGN_PATTERNS.md) | Pattern usage |
| [DATABASE.md](DATABASE.md) | Schema and ERD |
| [ALGORITHMS.md](ALGORITHMS.md) | Algorithm analysis |
| [TESTING.md](TESTING.md) | Test strategy |
| [INSTALLATION.md](INSTALLATION.md) | Setup guide |
| [USER_GUIDE.md](USER_GUIDE.md) | End-user guide |
| [PROJECT_AUDIT.md](PROJECT_AUDIT.md) | Requirement checklist |

Full knowledge base: [docs/](docs/)

---

## Future Work

- REST API layer (Flask/FastAPI)
- PostgreSQL adapter via repository abstraction
- Role-based authentication
- Web frontend (React)
- Email notifications on enrollment

See [ROADMAP.md](ROADMAP.md).

---

## License

MIT License — see [LICENSE](LICENSE).

---

## Acknowledgements

Capstone assignment by **Suganthan S**. Built following layered architecture, SOLID principles, and clean code practices.
