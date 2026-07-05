# System Architecture

See also: [../../ARCHITECTURE.md](../../ARCHITECTURE.md)

## Layers

1. **Presentation** — Tkinter GUI with MVC controllers
2. **Service** — Business logic orchestration
3. **Repository** — Data access abstraction
4. **Database** — SQLite persistence
5. **Domain** — Models, algorithms, patterns (framework-independent)

## Key Design Decisions

- **Adjacency list** over matrix for sparse prerequisite graphs
- **Repository pattern** for database swap capability
- **Observer pattern** for reactive GUI updates
- **Strategy pattern** for extensible path algorithms
- **Service container** for dependency injection

## Extension Points

- Add new `PathFindingStrategy` implementations
- Implement new `Repository` for PostgreSQL
- Register new `ProgressObserver` for notifications
- Replace GUI with Flask/React without changing services
