# LMPTS — Complete Project Guide

**Repository:** https://github.com/thiyagu26v/LMPTS  
**Author:** Suganthan S  
**Project:** Learning Management & Prerequisite Tracking System (Capstone)

---

## Table of Contents

1. [What Is This Project?](#1-what-is-this-project)
2. [Why Is It Useful?](#2-why-is-it-useful)
3. [Clone from GitHub](#3-clone-from-github)
4. [Install and Run](#4-install-and-run)
5. [How to Verify It Works](#5-how-to-verify-it-works)
6. [How to Use the Application](#6-how-to-use-the-application)
7. [System Architecture](#7-system-architecture)
8. [Design Patterns Used](#8-design-patterns-used)
9. [Backend File-by-File Reference](#9-backend-file-by-file-reference)
10. [Database Schema](#10-database-schema)
11. [Algorithms Implemented](#11-algorithms-implemented)
12. [Testing](#12-testing)
13. [Project Folder Structure](#13-project-folder-structure)

---

## 1. What Is This Project?

**LMPTS** (Learning Management & Prerequisite Tracking System) is a desktop application that helps educational institutions manage:

- **Courses** — catalog with difficulty, duration, instructor, status
- **Prerequisites** — rules like "CS102 requires CS101"
- **Learners** — student profiles and progress
- **Enrollments** — who is enrolled in what, with completion scores
- **Learning paths** — optimal course sequences from one course to another
- **Analytics** — completion rates, bottlenecks, system metrics

### Real-World Problem It Solves

Universities and training programs struggle with:

| Problem | LMPTS Solution |
|---------|----------------|
| Students enroll without completing prerequisites | Blocks enrollment until prerequisites are completed |
| Circular dependencies (A→B→C→A) | Detects and prevents cycles when adding prerequisites |
| No clear learning order | Computes shortest/optimized paths between courses |
| Limited progress visibility | Tracks completion rates and suggests next courses |

### System Actors

| Role | What They Do |
|------|--------------|
| **Administrator** | Create courses, define prerequisites, publish courses |
| **Instructor** | View learner progress and enrollments |
| **Learner** | Enroll in courses, track progress, complete courses |
| **Analyst** | View reports, completion stats, bottlenecks |

---

## 2. Why Is It Useful?

### For the Capstone Assignment

Demonstrates mastery of:

- **OOP** — inheritance, encapsulation, polymorphism, abstraction
- **Data structures** — graphs, sets, dictionaries, queues, deques
- **Algorithms** — BFS, DFS, cycle detection, topological sort
- **Design patterns** — Repository, Factory, Strategy, Observer, Singleton
- **Software engineering** — layered architecture, testing, documentation

### For Real Use (Demo Scale)

Works as a functional prototype for course prerequisite management with a GUI, SQLite database, and 95 automated tests.

---

## 3. Clone from GitHub

### Prerequisites

- **Git** installed — https://git-scm.com/
- **Python 3.10+** — https://www.python.org/downloads/
- **pip** (comes with Python)

### Clone Commands

```bash
# Clone the repository
git clone https://github.com/thiyagu26v/LMPTS.git

# Enter the project folder
cd LMPTS
```

### Windows (PowerShell)

```powershell
git clone https://github.com/thiyagu26v/LMPTS.git
cd LMPTS
```

### What You Get

```
LMPTS/
├── lmpts/          # Application source code
├── tests/          # 95 automated tests
├── docs/           # Documentation and knowledge base
├── main.py         # Application entry point
├── requirements.txt
├── README.md
└── ...
```

---

## 4. Install and Run

### Step 1 — Create Virtual Environment (Recommended)

```bash
python -m venv venv
```

**Windows:**
```powershell
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### Step 2 — Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3 — Run the Application

```bash
python main.py
```

The GUI window opens with **4 tabs**:

1. **Admin Panel** — course and prerequisite management
2. **Learner Portal** — enrollment and progress
3. **Learning Paths** — path finding between courses
4. **Analytics Dashboard** — reports and metrics

### First Run

On first launch, the app automatically:

1. Creates `data/lmpts.db` (SQLite database)
2. Runs migration script (`001_initial_schema.sql`)
3. Loads **seed data**:
   - 8 courses (CS101, CS102, CS201, CS301, MATH101, MATH201, WEB101, DB201)
   - 3 learners (L001, L002, L003)
   - Prerequisite chains and sample enrollments

---

## 5. How to Verify It Works

### Option A — Run All Tests (Recommended)

```bash
python -m pytest tests/ -v
```

**Expected:** `95 passed`

### Option B — Run with Coverage

```bash
python -m pytest tests/ --cov=lmpts --cov-report=term-missing
```

**Expected:** ~84% coverage (minimum required: 80%)

### Option C — Backend Smoke Test (No GUI)

```bash
python -c "from lmpts.services.container import ServiceContainer; c=ServiceContainer(); m=c.analytics_service.get_system_metrics(); print('Courses:', m.total_courses, '| Learners:', m.total_learners, '| Enrollments:', m.total_enrollments)"
```

**Expected output:**
```
Courses: 8 | Learners: 3 | Enrollments: 4
```

### Option D — Manual GUI Checks

| Tab | Action | Expected |
|-----|--------|----------|
| Admin Panel | View course table | 8 courses listed |
| Admin Panel | Select CS301 | Shows prerequisites |
| Learner Portal | Select L001, Load Progress | Progress bar and enrollments |
| Learner Portal | Validate CS301 for L001 | Error: missing prerequisites |
| Learning Paths | CS101 → CS301, Find Path | Valid path displayed |
| Analytics | Refresh Analytics | Metrics and completion table |

---

## 6. How to Use the Application

### 6.1 Admin Panel — Course Management

#### Create a Course

1. Fill in:
   - **Code:** e.g. `PY101`
   - **Name:** e.g. `Python Basics`
   - **Description:** Course description
   - **Difficulty:** beginner / intermediate / advanced / expert
   - **Duration (hrs):** e.g. `30`
   - **Instructor:** e.g. `Dr. Smith`
2. Click **Create Course**
3. Select the course in the table → click **Publish** (only published courses allow enrollment)

#### Add Prerequisites

1. **Prerequisite:** course that must be completed first (e.g. `CS101`)
2. **Dependent:** course that requires it (e.g. `CS102`)
3. Click **Add**

The system **blocks circular dependencies** automatically.

#### Other Admin Actions

- **Search** — filter courses by code, name, or instructor
- **Delete** — remove course (cascades to prerequisites and enrollments)
- **Select a course** — view direct and transitive prerequisites below the form

---

### 6.2 Learner Portal — Student Actions

#### Register a New Learner

1. Enter **Learner ID**, **Name**, **Email**
2. Click **Register**

#### Use Sample Learners (Pre-loaded)

| ID | Name | Notes |
|----|------|-------|
| L001 | Alice Johnson | Completed CS101, in progress CS102 |
| L002 | Bob Williams | Completed CS101, MATH101 |
| L003 | Carol Davis | New learner |

#### Enroll in a Course

1. Select learner from dropdown
2. Enter **course code** (e.g. `CS102`)
3. Click **Validate** — shows if prerequisites are met
4. Click **Enroll** if validation passes

#### Complete a Course

1. Enter course code
2. Enter optional **score** (0–100)
3. Click **Mark Complete**

#### View Progress

- Click **Load Progress** for completion % and **Suggested courses**
- Right panel shows all enrollments with status and scores

#### Example Prerequisite Chain

To enroll in **CS301**, a learner must complete:

```
CS101 → CS102 → CS201 → CS301
         MATH101 ────────┘
```

The system enforces this automatically.

---

### 6.3 Learning Paths Tab

1. **Start:** e.g. `CS101`
2. **Target:** e.g. `CS301`
3. **Strategy:**
   - `shortest` — fewest courses (BFS)
   - `difficulty` — gradual difficulty increase
   - `minimum_duration` — least total hours
4. Click **Find Path** or **Find All Paths**

**Example output:**
```
CS101 → MATH101 → CS102 → CS201 → CS301
Total hours: 190
```

---

### 6.4 Analytics Dashboard

Click **Refresh Analytics** to view:

- Total courses, learners, enrollments
- System-wide completion rate
- Per-course completion statistics
- **Bottleneck courses** — high prerequisites + low completion

---

## 7. System Architecture

LMPTS uses **strict layered architecture**. Each layer only talks to the layer below it.

```
┌─────────────────────────────────────────┐
│  PRESENTATION LAYER (GUI)               │
│  lmpts/gui/main_window.py               │
│  lmpts/gui/controllers.py               │
│  - Tkinter windows, event handlers      │
└──────────────────┬──────────────────────┘
                   │ calls
┌──────────────────▼──────────────────────┐
│  SERVICE LAYER (Business Logic)         │
│  lmpts/services/*.py                    │
│  - Rule enforcement, orchestration      │
└──────────────────┬──────────────────────┘
                   │ uses
┌──────────────────▼──────────────────────┐
│  REPOSITORY LAYER (Data Access)         │
│  lmpts/data/repository.py               │
│  - CRUD abstractions (no SQL in services)│
└──────────────────┬──────────────────────┘
                   │ uses
┌──────────────────▼──────────────────────┐
│  DATABASE LAYER                         │
│  lmpts/data/database.py                 │
│  - SQLite connection (Singleton)        │
└──────────────────┬──────────────────────┘
                   │ stores
┌──────────────────▼──────────────────────┐
│  DOMAIN LAYER (Independent)             │
│  lmpts/core/*.py                        │
│  - Models, algorithms, patterns, errors │
│  - NEVER depends on GUI or database     │
└─────────────────────────────────────────┘
```

### Dependency Rules

| Rule | Meaning |
|------|---------|
| Domain → nothing | Models and algorithms are framework-independent |
| Services → Repositories + Domain | Business logic, no SQL |
| Repositories → Database | All SQL hidden here |
| GUI → Services only | Controllers call services, never repositories |

### Data Flow Example — Enrollment

```
User clicks "Enroll" in GUI
    → LearnerController.enroll()
        → EnrollmentService.enroll()
            → Validates learner exists (LearnerRepository)
            → Validates course is published (CourseRepository)
            → Checks prerequisites (PrerequisiteGraph)
            → Checks no duplicate (EnrollmentRepository)
            → Creates enrollment (EnrollmentRepository)
            → Notifies observers (AnalyticsService cache invalidation)
    → GUI shows success or error message
```

---

## 8. Design Patterns Used

| Pattern | File | Purpose |
|---------|------|---------|
| **Repository** | `data/repository.py` | Hide SQL from business logic |
| **Factory** | `core/patterns.py` | Create validated Course, Learner, Enrollment |
| **Strategy** | `core/patterns.py` | Swap path-finding algorithms at runtime |
| **Observer** | `core/patterns.py` | Notify analytics/GUI on enrollment events |
| **Singleton** | `data/database.py` | One shared database connection manager |

---

## 9. Backend File-by-File Reference

### Root Level

| File | Purpose |
|------|---------|
| `main.py` | **Entry point.** Sets up logging, creates `ServiceContainer`, launches `LMPTSApplication` GUI |
| `requirements.txt` | Python dependencies (pytest, pytest-cov, black, isort, flake8, mypy) |
| `pyproject.toml` | Project metadata, pytest config, coverage settings (80% minimum) |

---

### `lmpts/` — Application Package

| File | Purpose |
|------|---------|
| `lmpts/__init__.py` | Package init, version `1.0.0` |

---

### `lmpts/core/` — Domain Layer (No GUI/DB Dependencies)

| File | Purpose | Key Contents |
|------|---------|--------------|
| `core/__init__.py` | Exports enums and exceptions | Public API for domain |
| `core/enums.py` | Categorical values | `DifficultyLevel`, `CourseStatus`, `EnrollmentStatus` |
| `core/exceptions.py` | Custom error hierarchy | `CourseNotFoundError`, `CircularDependencyError`, `PrerequisiteNotMetError`, etc. |
| `core/models.py` | Domain entities (OOP) | `Course`, `Learner`, `Enrollment`, `PrerequisiteRelation`, `LearnerProgress`, `PathStatistics` |
| `core/algorithms.py` | Graph algorithms | `PrerequisiteGraph` class + helper functions |
| `core/patterns.py` | Design patterns | Repository ABC, Factories, Strategies, Observers, PathFinder |

#### `core/models.py` — Detail

| Class | Description |
|-------|-------------|
| `Identifiable` | Abstract base — requires `id` property |
| `TimestampedEntity` | Adds `created_at`, `updated_at` |
| `Course` | Course with private `_prerequisites` set, validation, publish/archive status |
| `Learner` | Student profile with email validation |
| `Enrollment` | Links learner to course, tracks status and score |
| `PrerequisiteRelation` | Immutable value object for prereq edges |
| `PathStatistics` | Hours, difficulty progression for a path |
| `LearnerProgress` | Aggregated completion metrics |

#### `core/algorithms.py` — Detail

| Class/Function | Description |
|----------------|-------------|
| `PrerequisiteGraph` | Directed graph with adjacency lists |
| `.add_edge()` | Add prerequisite with cycle detection |
| `.detect_cycle()` | DFS coloring algorithm |
| `.shortest_path()` | BFS shortest path |
| `.get_transitive_prerequisites()` | All required courses (BFS on reverse graph) |
| `.compute_course_levels()` | Hierarchy depth per course |
| `.topological_sort()` | Kahn's algorithm |
| `expand_path_with_prerequisites()` | Insert missing lateral prereqs into path |
| `recommend_available_courses()` | Suggest enrollable courses |
| `identify_bottleneck_courses()` | Find high-prereq, low-completion courses |
| `compute_graph_complexity()` | Depth, edge count, avg prerequisites |

#### `core/patterns.py` — Detail

| Class | Pattern | Description |
|-------|---------|-------------|
| `Repository[T]` | Repository | Abstract CRUD interface |
| `CourseFactory` | Factory | Creates validated Course |
| `LearnerFactory` | Factory | Creates validated Learner |
| `EnrollmentFactory` | Factory | Creates validated Enrollment |
| `PathFindingStrategy` | Strategy | Abstract path algorithm |
| `ShortestPathStrategy` | Strategy | BFS implementation |
| `DifficultyProgressiveStrategy` | Strategy | Order by difficulty rank |
| `MinimumDurationStrategy` | Strategy | Minimize total hours |
| `PathFinder` | Strategy | Context class to swap strategies |
| `ProgressObserver` | Observer | Interface for enrollment events |
| `Observable` | Observer | Register/notify observers |
| `GUIRefreshObserver` | Observer | Triggers GUI refresh callback |
| `LoggingObserver` | Observer | Logs events for audit |

---

### `lmpts/data/` — Data Access Layer

| File | Purpose | Key Contents |
|------|---------|--------------|
| `data/__init__.py` | Package init | |
| `data/database.py` | **Singleton** database manager | Connection, transactions, migrations, seed data |
| `data/repository.py` | **Repository** implementations | CRUD for all entities |
| `data/migrations/001_initial_schema.sql` | Database schema | Tables, indexes, constraints, foreign keys |

#### `data/database.py` — Detail

| Feature | Description |
|---------|-------------|
| `DatabaseManager` | Thread-safe Singleton |
| `.initialize()` | Runs migrations + seed if empty |
| `.transaction()` | Atomic commit/rollback context manager |
| `.fetchone()` / `.fetchall()` | Query helpers |
| `PRAGMA foreign_keys = ON` | Referential integrity enforced |
| Seed data | 8 courses, 3 learners, 7 prerequisite edges, 4 enrollments |

#### `data/repository.py` — Detail

| Class | Entity | Operations |
|-------|--------|------------|
| `CourseRepository` | Course | create, read, update, delete, list_all, search, list_by_status |
| `LearnerRepository` | Learner | create, read, update, delete, list_all, exists |
| `EnrollmentRepository` | Enrollment | create, read, update, delete, find_by_learner_and_course, list_completed |
| `PrerequisiteRepository` | PrerequisiteRelation | add, remove, list_all, get_all_edges |

---

### `lmpts/services/` — Business Logic Layer

| File | Purpose | Implements |
|------|---------|------------|
| `services/__init__.py` | Exports all services | |
| `services/container.py` | **Dependency injection** | Wires repos, graph, services together |
| `services/course_service.py` | Course + prerequisite management | **FR1, FR2** |
| `services/learner_service.py` | Learner registration + progress | **FR3** |
| `services/enrollment_service.py` | Enrollment + validation | **FR4** |
| `services/learning_path_service.py` | Path computation | **FR5** |
| `services/analytics_service.py` | Reports + metrics | **FR6** |

#### `services/course_service.py` — Detail

| Method | Description |
|--------|-------------|
| `create_course()` | Create with duplicate check |
| `update_course()` | Update metadata |
| `delete_course()` | Delete with cascade |
| `publish_course()` / `archive_course()` | Status changes |
| `add_prerequisite()` | Add edge with cycle detection |
| `remove_prerequisite()` | Remove edge |
| `get_transitive_prerequisites()` | All required courses |
| `get_course_levels()` | Hierarchy levels |
| `search_courses()` | Search by code/name/instructor |

#### `services/enrollment_service.py` — Detail

| Method | Description |
|--------|-------------|
| `enroll()` | Full validation + create enrollment |
| `complete_course()` | Mark completed with optional score |
| `drop_enrollment()` | Drop enrollment |
| `validate_enrollment()` | Check without persisting |
| `suggest_available_courses()` | Recommend next courses |
| Observer notifications | On create/complete |

#### `services/learning_path_service.py` — Detail

| Method | Description |
|--------|-------------|
| `find_shortest_path()` | BFS + expand prerequisites |
| `find_path_with_strategy()` | Use named strategy |
| `find_multiple_paths()` | Multiple suggestions |
| `validate_path()` | Check path against prereq rules |

#### `services/analytics_service.py` — Detail

| Method | Description |
|--------|-------------|
| `get_system_metrics()` | Totals, completion rate, graph depth |
| `get_course_completion_stats()` | Per-course stats |
| `get_bottleneck_courses()` | High-prereq, low-completion |
| `generate_report()` | Full cached report |
| Implements `ProgressObserver` | Cache invalidation on events |

---

### `lmpts/gui/` — Presentation Layer

| File | Purpose |
|------|---------|
| `gui/__init__.py` | Package init |
| `gui/controllers.py` | **MVC Controllers** — connect GUI to services, handle errors |
| `gui/main_window.py` | **Main window** — 4 tabs, tables, forms, status bar |

#### `gui/controllers.py` — Detail

| Controller | Handles |
|------------|---------|
| `AdminController` | Course CRUD, prerequisites |
| `LearnerController` | Register, enroll, complete, progress |
| `AnalyticsController` | Reports and metrics |
| `PathController` | Learning path finding |
| `BaseController` | Shared error handling |

#### `gui/main_window.py` — Detail

| Tab | Features |
|-----|----------|
| Admin Panel | Course form, prerequisite form, searchable course table |
| Learner Portal | Learner registration, enrollment validation, progress bar, enrollment table |
| Learning Paths | Start/target/strategy inputs, path results text area |
| Analytics Dashboard | System metrics text, completion table, bottleneck info |

---

### `lmpts/utils/` — Utilities

| File | Purpose |
|------|---------|
| `utils/logging_config.py` | Configures application logging to console/file |
| `utils/__init__.py` | Package init |

---

### `tests/` — Automated Tests (95 Tests)

| File | Tests |
|------|-------|
| `conftest.py` | Fixtures: temp DB, service container |
| `test_models.py` | Course, Learner, Enrollment validation |
| `test_algorithms.py` | Graph: BFS, DFS, cycles, paths |
| `test_patterns.py` | Factory, Strategy, Observer |
| `test_database.py` | Singleton, migrations, transactions |
| `test_repositories.py` | CRUD for all repositories |
| `test_services.py` | All service methods |
| `test_integration.py` | End-to-end workflows |
| `test_edge_cases.py` | Invalid inputs, performance |

---

## 10. Database Schema

### Tables

```
courses          learners         prerequisites       enrollments
─────────        ────────         ─────────────       ───────────
code (PK)        learner_id (PK)  id (PK)             id (PK)
name             name             prereq_code (FK)    learner_id (FK)
description      email (UNIQUE)   dependent_code (FK) course_code (FK)
difficulty                        UNIQUE(pair)        status
duration_hours                                          score
instructor                                              enrolled_at
status                                                  completed_at
```

### Prerequisite Chain (Seed Data)

```
CS101 ──→ CS102 ──→ CS201 ──→ CS301
              │
MATH101 ──────┘ (also required for CS201)

CS101 ──→ WEB101 ──→ DB201
MATH101 ──→ MATH201
```

---

## 11. Algorithms Implemented

| Algorithm | Complexity | Location | Used For |
|-----------|------------|----------|----------|
| Cycle detection (DFS) | O(V+E) | `core/algorithms.py` | Block invalid prerequisites |
| BFS shortest path | O(V+E) | `core/algorithms.py` | Learning path finding |
| Transitive prerequisites | O(V+E) | `core/algorithms.py` | Enrollment validation |
| Topological sort | O(V+E) | `core/algorithms.py` | Path expansion, difficulty strategy |
| Course level computation | O(V+E) | `core/algorithms.py` | Hierarchy depth |
| Bottleneck detection | O(V×P) | `core/algorithms.py` | Analytics |
| Course recommendation | O(C×P) | `core/algorithms.py` | Suggest available courses |

---

## 12. Testing

```bash
# Run all tests
python -m pytest tests/ -v

# With coverage
python -m pytest tests/ --cov=lmpts --cov-report=html:docs/reports/coverage_html
```

| Metric | Value |
|--------|-------|
| Total tests | 95 |
| Passed | 95 |
| Coverage | ~84% |
| Minimum required | 80% |

---

## 13. Project Folder Structure

```
LMPTS/
├── main.py                          # Entry point
├── requirements.txt                 # Dependencies
├── pyproject.toml                   # Project config
├── README.md                        # Project overview
├── COMPLETE_PROJECT_GUIDE.md        # This file
├── ARCHITECTURE.md                  # Architecture diagrams
├── DESIGN_PATTERNS.md               # Pattern documentation
├── DATABASE.md                      # Schema details
├── ALGORITHMS.md                    # Algorithm analysis
├── TESTING.md                       # Test guide
├── TEST_REPORT.md                   # Test results
├── PROJECT_AUDIT.md                 # Requirement checklist
├── USER_GUIDE.md                    # User manual
├── ADMIN_GUIDE.md                   # Admin manual
├── LEARNER_GUIDE.md                 # Learner manual
├── LICENSE                          # MIT License
│
├── lmpts/                           # Application package
│   ├── core/                        # Domain layer
│   │   ├── models.py                # Entities
│   │   ├── algorithms.py            # Graph algorithms
│   │   ├── patterns.py              # Design patterns
│   │   ├── exceptions.py            # Custom errors
│   │   └── enums.py                 # Enumerations
│   ├── data/                        # Data layer
│   │   ├── database.py              # SQLite Singleton
│   │   ├── repository.py            # Repositories
│   │   └── migrations/
│   │       └── 001_initial_schema.sql
│   ├── services/                    # Business logic
│   │   ├── container.py             # Dependency injection
│   │   ├── course_service.py        # FR1, FR2
│   │   ├── learner_service.py       # FR3
│   │   ├── enrollment_service.py    # FR4
│   │   ├── learning_path_service.py # FR5
│   │   └── analytics_service.py     # FR6
│   ├── gui/                         # Presentation
│   │   ├── main_window.py           # Tkinter GUI (FR7)
│   │   └── controllers.py           # MVC controllers
│   └── utils/
│       └── logging_config.py
│
├── tests/                           # 95 automated tests
│   ├── test_models.py
│   ├── test_algorithms.py
│   ├── test_patterns.py
│   ├── test_database.py
│   ├── test_repositories.py
│   ├── test_services.py
│   ├── test_integration.py
│   └── test_edge_cases.py
│
├── docs/                            # Knowledge base
│   ├── PROJECT_OVERVIEW.md
│   ├── DOMAIN_MODEL.md
│   ├── architecture/
│   └── reports/
│       └── coverage_html/           # HTML coverage report
│
└── data/                            # Created on first run
    └── lmpts.db                     # SQLite database
```

---

## Quick Reference Card

```bash
# Clone
git clone https://github.com/thiyagu26v/LMPTS.git && cd LMPTS

# Setup
pip install -r requirements.txt

# Run
python main.py

# Test
python -m pytest tests/ -v
```

| Sample Learner | Sample Path | Sample Validation |
|----------------|-------------|-------------------|
| L001, L002, L003 | CS101 → CS301 | Enroll L001 in CS301 → blocked |

---

**GitHub:** https://github.com/thiyagu26v/LMPTS  
**Author:** Suganthan S  
**Status:** Capstone complete — 95 tests passing, 84% coverage
