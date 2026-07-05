"""Learning path computation business logic."""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Tuple

from lmpts.core.algorithms import PrerequisiteGraph, compute_path_statistics, expand_path_with_prerequisites
from lmpts.core.exceptions import CourseNotFoundError, ValidationError
from lmpts.core.models import PathStatistics
from lmpts.core.patterns import (
    DifficultyProgressiveStrategy,
    MinimumDurationStrategy,
    PathFinder,
    PathFindingStrategy,
    ShortestPathStrategy,
)
from lmpts.data.repository import CourseRepository, PrerequisiteRepository

logger = logging.getLogger(__name__)


class LearningPathService:
    """Service for learning path computation (FR5)."""

    STRATEGIES: Dict[str, PathFindingStrategy] = {
        "shortest": ShortestPathStrategy(),
        "difficulty": DifficultyProgressiveStrategy(),
        "minimum_duration": MinimumDurationStrategy(),
    }

    def __init__(
        self,
        course_repo: CourseRepository,
        prerequisite_repo: PrerequisiteRepository,
        graph: PrerequisiteGraph,
    ) -> None:
        self._course_repo = course_repo
        self._prerequisite_repo = prerequisite_repo
        self._graph = graph
        self._path_finder = PathFinder(ShortestPathStrategy())

    def set_graph(self, graph: PrerequisiteGraph) -> None:
        self._graph = graph

    def _get_course_metadata(
        self,
    ) -> Tuple[Dict[str, float], Dict[str, int]]:
        durations: Dict[str, float] = {}
        difficulties: Dict[str, int] = {}
        for course in self._course_repo.list_all():
            durations[course.code] = course.duration_hours
            difficulties[course.code] = course.difficulty.numeric_rank
        return durations, difficulties

    def find_shortest_path(
        self, start: str, target: str
    ) -> Tuple[Optional[List[str]], Optional[PathStatistics]]:
        """Find shortest learning path using BFS."""
        self._validate_courses_exist(start, target)
        durations, difficulties = self._get_course_metadata()
        self._path_finder.set_strategy(ShortestPathStrategy())
        path, stats = self._path_finder.find_path_with_stats(
            self._graph, start, target, durations, difficulties
        )
        return self._expand_and_restat(path, stats, durations, difficulties)

    def _expand_and_restat(
        self,
        path: Optional[List[str]],
        stats: Optional[PathStatistics],
        durations: Dict[str, float],
        difficulties: Dict[str, int],
    ) -> Tuple[Optional[List[str]], Optional[PathStatistics]]:
        if not path:
            return None, None
        expanded = expand_path_with_prerequisites(path, self._graph)
        new_stats = compute_path_statistics(expanded, durations, difficulties)
        return expanded, new_stats

    def find_path_with_strategy(
        self, start: str, target: str, strategy_name: str = "shortest"
    ) -> Tuple[Optional[List[str]], Optional[PathStatistics]]:
        """Find path using named strategy."""
        self._validate_courses_exist(start, target)
        strategy = self.STRATEGIES.get(strategy_name)
        if not strategy:
            raise ValidationError(
                f"Unknown strategy '{strategy_name}'. "
                f"Available: {', '.join(self.STRATEGIES.keys())}"
            )
        durations, difficulties = self._get_course_metadata()
        self._path_finder.set_strategy(strategy)
        path, stats = self._path_finder.find_path_with_stats(
            self._graph, start, target, durations, difficulties
        )
        return self._expand_and_restat(path, stats, durations, difficulties)

    def find_multiple_paths(
        self, start: str, target: str, max_paths: int = 5
    ) -> List[Tuple[List[str], PathStatistics]]:
        """Provide multiple path suggestions with different strategies."""
        results: List[Tuple[List[str], PathStatistics]] = []
        seen_paths: set[tuple] = set()

        for name in self.STRATEGIES:
            path, stats = self.find_path_with_strategy(start, target, name)
            if path and stats:
                path_key = tuple(path)
                if path_key not in seen_paths:
                    seen_paths.add(path_key)
                    results.append((path, stats))

        all_paths = self._graph.all_paths(start, target, max_paths=max_paths)
        durations, difficulties = self._get_course_metadata()
        for path in all_paths:
            expanded = expand_path_with_prerequisites(path, self._graph)
            path_key = tuple(expanded)
            if path_key not in seen_paths:
                seen_paths.add(path_key)
                stats = compute_path_statistics(expanded, durations, difficulties)
                results.append((expanded, stats))

        return results[:max_paths]

    def validate_path(self, path: List[str]) -> Tuple[bool, str]:
        """Validate proposed learning path against prerequisite constraints."""
        if not path:
            return False, "Path cannot be empty"
        if len(path) != len(set(path)):
            return False, "Path contains duplicate courses"

        for i, course in enumerate(path):
            if not self._course_repo.exists(course):
                return False, f"Course {course} not found"
            if i == 0:
                continue
            prereqs = self._graph.get_transitive_prerequisites(course)
            prior = set(path[:i])
            missing = prereqs - prior
            if missing:
                return False, (
                    f"Course {course} requires {sorted(missing)} "
                    f"before position {i + 1}"
                )
        return True, "Path is valid"

    def _validate_courses_exist(self, start: str, target: str) -> None:
        start_code = start.strip().upper()
        target_code = target.strip().upper()
        if not self._course_repo.exists(start_code):
            raise CourseNotFoundError(f"Start course {start_code} not found")
        if not self._course_repo.exists(target_code):
            raise CourseNotFoundError(f"Target course {target_code} not found")

    def get_available_strategies(self) -> List[str]:
        return list(self.STRATEGIES.keys())
