"""Graph algorithms for prerequisite management and path finding."""

from __future__ import annotations

from collections import deque
from typing import Dict, List, Optional, Set, Tuple

from lmpts.core.exceptions import CircularDependencyError


class PrerequisiteGraph:
    """
    Directed graph for prerequisite relationships using adjacency lists.

    Edge direction: prerequisite -> dependent (must complete prereq before dependent).
    Time complexity: add_edge O(V+E) cycle check, BFS O(V+E), DFS O(V+E).
    """

    def __init__(self) -> None:
        self._adjacency: Dict[str, Set[str]] = {}
        self._reverse: Dict[str, Set[str]] = {}

    def add_node(self, course_code: str) -> None:
        """Register a course node in the graph."""
        code = course_code.strip().upper()
        if code not in self._adjacency:
            self._adjacency[code] = set()
            self._reverse[code] = set()

    def add_edge(self, prerequisite: str, dependent: str) -> None:
        """
        Add prerequisite edge with cycle detection.

        Raises CircularDependencyError if edge would create a cycle.
        Complexity: O(V + E) using DFS reachability check.
        """
        prereq = prerequisite.strip().upper()
        dep = dependent.strip().upper()
        if prereq == dep:
            raise CircularDependencyError(
                f"Self-prerequisite not allowed for course {dep}"
            )
        self.add_node(prereq)
        self.add_node(dep)
        if self._would_create_cycle(prereq, dep):
            raise CircularDependencyError(
                f"Adding prerequisite {prereq} -> {dep} would create a cycle"
            )
        self._adjacency[prereq].add(dep)
        self._reverse[dep].add(prereq)

    def remove_edge(self, prerequisite: str, dependent: str) -> None:
        """Remove a prerequisite edge."""
        prereq = prerequisite.strip().upper()
        dep = dependent.strip().upper()
        if prereq in self._adjacency:
            self._adjacency[prereq].discard(dep)
        if dep in self._reverse:
            self._reverse[dep].discard(prereq)

    def _would_create_cycle(self, prerequisite: str, dependent: str) -> bool:
        """Check if dependent can reach prerequisite (would form cycle)."""
        return self._has_path_dfs(dependent, prerequisite)

    def _has_path_dfs(self, start: str, target: str) -> bool:
        """DFS path existence check. O(V + E)."""
        if start == target:
            return True
        visited: Set[str] = set()
        stack = [start]
        while stack:
            node = stack.pop()
            if node in visited:
                continue
            visited.add(node)
            if node == target:
                return True
            for neighbor in self._adjacency.get(node, set()):
                if neighbor not in visited:
                    stack.append(neighbor)
        return False

    def detect_cycle(self) -> Optional[List[str]]:
        """
        Detect cycle using DFS coloring algorithm.

        Returns cycle path if found, else None. O(V + E).
        """
        white, gray, black = 0, 1, 2
        color: Dict[str, int] = {n: white for n in self._adjacency}
        parent: Dict[str, Optional[str]] = {n: None for n in self._adjacency}

        def dfs(node: str) -> Optional[List[str]]:
            color[node] = gray
            for neighbor in self._adjacency.get(node, set()):
                if color.get(neighbor, white) == gray:
                    cycle = [neighbor, node]
                    current = node
                    while current != neighbor and parent.get(current):
                        current = parent[current]  # type: ignore[assignment]
                        cycle.append(current)
                    cycle.reverse()
                    return cycle
                if color.get(neighbor, white) == white:
                    parent[neighbor] = node
                    result = dfs(neighbor)
                    if result:
                        return result
            color[node] = black
            return None

        for node in list(self._adjacency.keys()):
            if color.get(node, white) == white:
                cycle = dfs(node)
                if cycle:
                    return cycle
        return None

    def get_direct_prerequisites(self, course_code: str) -> Set[str]:
        """Return direct prerequisites for a course. O(1) lookup."""
        return self._reverse.get(course_code.strip().upper(), set()).copy()

    def get_direct_dependents(self, course_code: str) -> Set[str]:
        """Return courses that depend on this course."""
        return self._adjacency.get(course_code.strip().upper(), set()).copy()

    def get_transitive_prerequisites(self, course_code: str) -> Set[str]:
        """
        Return all transitive prerequisites using BFS on reverse graph.

        Complexity: O(V + E).
        """
        code = course_code.strip().upper()
        result: Set[str] = set()
        queue: deque[str] = deque(self._reverse.get(code, set()))
        while queue:
            node = queue.popleft()
            if node in result:
                continue
            result.add(node)
            queue.extend(self._reverse.get(node, set()) - result)
        return result

    def get_transitive_dependents(self, course_code: str) -> Set[str]:
        """Return all courses transitively depending on this course."""
        code = course_code.strip().upper()
        result: Set[str] = set()
        queue: deque[str] = deque(self._adjacency.get(code, set()))
        while queue:
            node = queue.popleft()
            if node in result:
                continue
            result.add(node)
            queue.extend(self._adjacency.get(node, set()) - result)
        return result

    def compute_course_levels(self) -> Dict[str, int]:
        """
        Compute hierarchy level for each course (longest path from root).

        Root courses (no prerequisites) are level 0. O(V + E).
        """
        in_degree: Dict[str, int] = {
            n: len(self._reverse.get(n, set())) for n in self._adjacency
        }
        levels: Dict[str, int] = {n: 0 for n in self._adjacency}
        queue: deque[str] = deque(n for n, d in in_degree.items() if d == 0)

        while queue:
            node = queue.popleft()
            for dependent in self._adjacency.get(node, set()):
                levels[dependent] = max(levels[dependent], levels[node] + 1)
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        return levels

    def shortest_path(self, start: str, target: str) -> Optional[List[str]]:
        """
        BFS shortest learning path from start to target.

        Complexity: O(V + E).
        """
        start_code = start.strip().upper()
        target_code = target.strip().upper()
        if start_code == target_code:
            return [start_code]
        if start_code not in self._adjacency or target_code not in self._adjacency:
            return None

        visited: Set[str] = {start_code}
        queue: deque[Tuple[str, List[str]]] = deque([(start_code, [start_code])])

        while queue:
            node, path = queue.popleft()
            for neighbor in self._adjacency.get(node, set()):
                if neighbor == target_code:
                    return path + [neighbor]
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        return None

    def all_paths(
        self, start: str, target: str, max_paths: int = 10
    ) -> List[List[str]]:
        """Find multiple paths using DFS with limit."""
        start_code = start.strip().upper()
        target_code = target.strip().upper()
        paths: List[List[str]] = []

        def dfs(node: str, path: List[str], visited: Set[str]) -> None:
            if len(paths) >= max_paths:
                return
            if node == target_code:
                paths.append(path.copy())
                return
            for neighbor in self._adjacency.get(node, set()):
                if neighbor not in visited:
                    visited.add(neighbor)
                    path.append(neighbor)
                    dfs(neighbor, path, visited)
                    path.pop()
                    visited.discard(neighbor)

        if start_code in self._adjacency:
            dfs(start_code, [start_code], {start_code})
        return paths

    def topological_sort(self) -> List[str]:
        """Kahn's algorithm for topological ordering. O(V + E)."""
        in_degree: Dict[str, int] = {
            n: len(self._reverse.get(n, set())) for n in self._adjacency
        }
        queue: deque[str] = deque(n for n, d in in_degree.items() if d == 0)
        result: List[str] = []

        while queue:
            node = queue.popleft()
            result.append(node)
            for dependent in self._adjacency.get(node, set()):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        if len(result) != len(self._adjacency):
            return []
        return result

    def get_nodes(self) -> Set[str]:
        return set(self._adjacency.keys())

    def get_edge_count(self) -> int:
        return sum(len(deps) for deps in self._adjacency.values())

    def load_from_edges(self, edges: List[Tuple[str, str]]) -> None:
        """Rebuild graph from edge list."""
        self._adjacency.clear()
        self._reverse.clear()
        for prereq, dep in edges:
            self.add_edge(prereq, dep)

    @property
    def adjacency(self) -> Dict[str, Set[str]]:
        return {k: v.copy() for k, v in self._adjacency.items()}


def expand_path_with_prerequisites(
    path: List[str], graph: PrerequisiteGraph
) -> List[str]:
    """
    Expand a path to include all transitive prerequisites in valid order.

    Uses topological sort to insert missing prerequisites. O(V + E).
    """
    if not path:
        return []

    needed: Set[str] = set(path)
    for course in path:
        needed.update(graph.get_transitive_prerequisites(course))

    topo = graph.topological_sort()
    if topo:
        expanded = [c for c in topo if c in needed]
        if expanded and expanded[-1] == path[-1]:
            return expanded

    result: List[str] = []
    seen: Set[str] = set()
    for course in path:
        for prereq in sorted(graph.get_transitive_prerequisites(course)):
            if prereq not in seen:
                result.append(prereq)
                seen.add(prereq)
        if course not in seen:
            result.append(course)
            seen.add(course)
    return result


def compute_path_statistics(
    path: List[str],
    course_durations: Dict[str, float],
    course_difficulties: Dict[str, int],
) -> "PathStatistics":
    """Calculate statistics for a learning path."""
    from lmpts.core.models import PathStatistics

    total_hours = sum(course_durations.get(c, 0) for c in path)
    difficulties = [course_difficulties.get(c, 1) for c in path]
    avg = sum(difficulties) / len(difficulties) if difficulties else 0.0
    return PathStatistics(
        total_hours=total_hours,
        course_count=len(path),
        difficulty_progression=difficulties,
        average_difficulty=avg,
    )


def recommend_available_courses(
    all_courses: Set[str],
    completed: Set[str],
    graph: PrerequisiteGraph,
    published_only: Set[str] | None = None,
) -> Set[str]:
    """
    Suggest courses where all prerequisites are completed.

    Complexity: O(C * P) where C = courses, P = avg prerequisites.
    """
    available: Set[str] = set()
    for course in all_courses:
        if course in completed:
            continue
        if published_only is not None and course not in published_only:
            continue
        prereqs = graph.get_transitive_prerequisites(course)
        if prereqs.issubset(completed):
            available.add(course)
    return available


def identify_bottleneck_courses(
    graph: PrerequisiteGraph,
    completion_rates: Dict[str, float],
    threshold: float = 0.5,
) -> List[Tuple[str, int, float]]:
    """
    Identify courses with high prerequisite count and low completion.

    Returns list of (course_code, prereq_count, completion_rate) sorted by impact.
    """
    bottlenecks: List[Tuple[str, int, float]] = []
    for course in graph.get_nodes():
        prereq_count = len(graph.get_transitive_prerequisites(course))
        rate = completion_rates.get(course, 0.0)
        if prereq_count >= 2 and rate < threshold:
            bottlenecks.append((course, prereq_count, rate))
    bottlenecks.sort(key=lambda x: (-x[1], x[2]))
    return bottlenecks


def compute_graph_depth(graph: PrerequisiteGraph) -> int:
    """Return maximum course level in prerequisite hierarchy."""
    levels = graph.compute_course_levels()
    return max(levels.values()) if levels else 0


def compute_graph_complexity(graph: PrerequisiteGraph) -> Dict[str, int | float]:
    """Analyze prerequisite structure complexity."""
    nodes = len(graph.get_nodes())
    edges = graph.get_edge_count()
    depth = compute_graph_depth(graph)
    avg_prereqs = edges / nodes if nodes else 0.0
    return {
        "node_count": nodes,
        "edge_count": edges,
        "max_depth": depth,
        "average_prerequisites": avg_prereqs,
    }
