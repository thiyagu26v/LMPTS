"""Unit tests for graph algorithms."""

import pytest

from lmpts.core.algorithms import (
    PrerequisiteGraph,
    compute_graph_complexity,
    compute_path_statistics,
    identify_bottleneck_courses,
    recommend_available_courses,
)
from lmpts.core.exceptions import CircularDependencyError


class TestPrerequisiteGraph:
    def test_add_edge(self):
        g = PrerequisiteGraph()
        g.add_edge("A", "B")
        assert g.get_direct_prerequisites("B") == {"A"}
        assert g.get_direct_dependents("A") == {"B"}

    def test_self_edge_raises(self):
        g = PrerequisiteGraph()
        with pytest.raises(CircularDependencyError):
            g.add_edge("A", "A")

    def test_cycle_detection_on_add(self):
        g = PrerequisiteGraph()
        g.add_edge("A", "B")
        g.add_edge("B", "C")
        with pytest.raises(CircularDependencyError):
            g.add_edge("C", "A")

    def test_detect_cycle(self):
        g = PrerequisiteGraph()
        g.add_node("A")
        g.add_node("B")
        g.add_node("C")
        g._adjacency["A"] = {"B"}
        g._adjacency["B"] = {"C"}
        g._adjacency["C"] = {"A"}
        g._reverse["B"] = {"A"}
        g._reverse["C"] = {"B"}
        g._reverse["A"] = {"C"}
        cycle = g.detect_cycle()
        assert cycle is not None

    def test_transitive_prerequisites(self):
        g = PrerequisiteGraph()
        g.add_edge("A", "B")
        g.add_edge("B", "C")
        assert g.get_transitive_prerequisites("C") == {"A", "B"}

    def test_shortest_path_bfs(self):
        g = PrerequisiteGraph()
        g.add_edge("A", "B")
        g.add_edge("B", "C")
        g.add_edge("A", "C")
        path = g.shortest_path("A", "C")
        assert path == ["A", "C"]

    def test_shortest_path_no_path(self):
        g = PrerequisiteGraph()
        g.add_node("A")
        g.add_node("B")
        assert g.shortest_path("A", "B") is None

    def test_course_levels(self):
        g = PrerequisiteGraph()
        g.add_edge("A", "B")
        g.add_edge("B", "C")
        levels = g.compute_course_levels()
        assert levels["A"] == 0
        assert levels["B"] == 1
        assert levels["C"] == 2

    def test_topological_sort(self):
        g = PrerequisiteGraph()
        g.add_edge("A", "B")
        g.add_edge("B", "C")
        topo = g.topological_sort()
        assert topo.index("A") < topo.index("B") < topo.index("C")

    def test_all_paths(self):
        g = PrerequisiteGraph()
        g.add_edge("A", "B")
        g.add_edge("B", "D")
        g.add_edge("A", "C")
        g.add_edge("C", "D")
        paths = g.all_paths("A", "D")
        assert len(paths) >= 2

    def test_remove_edge(self):
        g = PrerequisiteGraph()
        g.add_edge("A", "B")
        g.remove_edge("A", "B")
        assert g.get_direct_prerequisites("B") == set()


class TestRecommendAvailable:
    def test_recommend_with_completed_prereqs(self):
        g = PrerequisiteGraph()
        g.add_edge("A", "B")
        available = recommend_available_courses({"A", "B"}, {"A"}, g)
        assert "B" in available
        assert "A" not in available

    def test_no_available_without_prereqs(self):
        g = PrerequisiteGraph()
        g.add_edge("A", "B")
        available = recommend_available_courses({"A", "B"}, set(), g)
        assert "B" not in available
        assert "A" in available


class TestPathStatistics:
    def test_compute_stats(self):
        stats = compute_path_statistics(
            ["A", "B"],
            {"A": 10.0, "B": 20.0},
            {"A": 1, "B": 2},
        )
        assert stats.total_hours == 30.0
        assert stats.course_count == 2


class TestBottlenecks:
    def test_identify_bottlenecks(self):
        g = PrerequisiteGraph()
        g.add_edge("A", "B")
        g.add_edge("C", "B")
        rates = {"B": 0.2, "A": 0.9, "C": 0.8}
        bottlenecks = identify_bottleneck_courses(g, rates, threshold=0.5)
        assert any(b[0] == "B" for b in bottlenecks)


class TestGraphComplexity:
    def test_complexity_metrics(self):
        g = PrerequisiteGraph()
        g.add_edge("A", "B")
        g.add_edge("B", "C")
        metrics = compute_graph_complexity(g)
        assert metrics["node_count"] == 3
        assert metrics["edge_count"] == 2
        assert metrics["max_depth"] == 2
