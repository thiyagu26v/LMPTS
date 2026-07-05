# Algorithms

## PrerequisiteGraph

Directed graph with adjacency list representation.

**Edge direction:** `prerequisite → dependent`

### Cycle Detection

**Algorithm:** DFS with coloring (WHITE/GRAY/BLACK)  
**On add_edge:** DFS reachability check from dependent to prerequisite  
**Complexity:** O(V + E)

### BFS Shortest Path

**Algorithm:** Breadth-first search with path tracking  
**Complexity:** O(V + E)  
**Use case:** Minimum course count path between two courses

### Transitive Prerequisites

**Algorithm:** BFS on reverse adjacency list  
**Complexity:** O(V + E)  
**Use case:** Full prerequisite chain for enrollment validation

### Course Level Computation

**Algorithm:** Modified Kahn's topological sort with level tracking  
**Complexity:** O(V + E)  
**Use case:** Hierarchy depth analysis

### Path Expansion

**Algorithm:** Topological sort filtered to needed nodes  
**Complexity:** O(V + E)  
**Use case:** Insert lateral prerequisites (e.g., MATH101 before CS201)

## Analytics Algorithms

| Function | Complexity | Purpose |
|----------|------------|---------|
| `recommend_available_courses` | O(C × P) | Suggest enrollable courses |
| `identify_bottleneck_courses` | O(V × P) | Find high-prereq, low-completion courses |
| `compute_graph_complexity` | O(V + E) | Structure depth and density metrics |
| `compute_path_statistics` | O(P) | Hours, difficulty progression |

## Strategy Algorithms

1. **ShortestPathStrategy** — BFS
2. **DifficultyProgressiveStrategy** — Topological sort by difficulty rank
3. **MinimumDurationStrategy** — DFS all paths, minimize total hours

## Performance Targets (NFR2)

| Operation | Target | Implementation |
|-----------|--------|----------------|
| Course lookup | O(1) | Dict/hash by code |
| Prerequisite validation | O(n) | Set membership + BFS |
| Path finding | O(V + E) | BFS/DFS |
| Scale | 10K courses | Adjacency list (sparse) |

## Test Coverage

All algorithms have dedicated unit tests in `tests/test_algorithms.py`.

Performance test: 100-node chain path finding in `tests/test_edge_cases.py`.
