# Design Patterns

## Repository Pattern

**Location:** `lmpts/data/repository.py`, `lmpts/core/patterns.py`

Abstracts all database operations behind interfaces. Services depend on repositories, not SQL.

```python
class Repository(ABC, Generic[T]):
    @abstractmethod
    def create(self, entity: T) -> T: ...
    @abstractmethod
    def read(self, entity_id: str) -> Optional[T]: ...
```

**Benefit:** Swap SQLite → PostgreSQL without changing services.

## Factory Pattern

**Location:** `lmpts/core/patterns.py`

Centralizes entity creation with validation:

- `CourseFactory.create()` — validates before returning Course
- `LearnerFactory.create()` — validates email, ID
- `EnrollmentFactory.create()` — validates enrollment fields

**Benefit:** Single point of validation; invalid objects cannot be created.

## Strategy Pattern

**Location:** `lmpts/core/patterns.py`

Pluggable path-finding algorithms:

| Strategy | Class | Behavior |
|----------|-------|----------|
| Shortest | `ShortestPathStrategy` | BFS minimum hops |
| Difficulty | `DifficultyProgressiveStrategy` | Gradual difficulty increase |
| Min Duration | `MinimumDurationStrategy` | Minimize total hours |

```python
finder = PathFinder(ShortestPathStrategy())
finder.set_strategy(DifficultyProgressiveStrategy())  # Runtime swap
```

**Benefit:** Open/Closed Principle — add new strategies without modifying existing code.

## Observer Pattern

**Location:** `lmpts/core/patterns.py`, `lmpts/services/enrollment_service.py`

Decouples event producers from consumers:

- `EnrollmentService` notifies on enrollment create/complete
- `AnalyticsService` invalidates cache on events
- `GUIRefreshObserver` triggers UI refresh

**Benefit:** GUI updates automatically when data changes.

## Singleton Pattern

**Location:** `lmpts/data/database.py`

Thread-safe singleton for database connection management:

```python
db = DatabaseManager()  # Always same instance
```

**Benefit:** Single connection pool, consistent transaction state.

## Data Structures Used

| Structure | Usage | Why |
|-----------|-------|-----|
| `Set` | Prerequisites | O(1) membership testing |
| `Dict` | Adjacency lists | O(1) node lookup |
| `Deque` | BFS queue | O(1) append/pop |
| Directed Graph | Prerequisite network | Models course dependencies |
| Adjacency List | Graph storage | Space-efficient for sparse graphs |
