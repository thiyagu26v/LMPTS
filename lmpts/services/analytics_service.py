"""Analytics and reporting business logic."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from lmpts.core.algorithms import (
    PrerequisiteGraph,
    compute_graph_complexity,
    identify_bottleneck_courses,
)
from lmpts.core.enums import EnrollmentStatus
from lmpts.core.patterns import ProgressObserver
from lmpts.data.repository import (
    CourseRepository,
    EnrollmentRepository,
    LearnerRepository,
    PrerequisiteRepository,
)

logger = logging.getLogger(__name__)


@dataclass
class SystemMetrics:
    """System-wide analytics metrics."""

    total_courses: int = 0
    published_courses: int = 0
    total_learners: int = 0
    total_enrollments: int = 0
    completed_enrollments: int = 0
    completion_rate: float = 0.0
    graph_depth: int = 0
    graph_edges: int = 0
    average_prerequisites: float = 0.0


@dataclass
class CourseCompletionStats:
    """Completion statistics for a single course."""

    course_code: str
    course_name: str
    total_enrollments: int
    completed_count: int
    completion_rate: float
    average_score: Optional[float] = None


@dataclass
class AnalyticsReport:
    """Full analytics report."""

    system_metrics: SystemMetrics
    course_stats: List[CourseCompletionStats] = field(default_factory=list)
    bottlenecks: List[Tuple[str, int, float]] = field(default_factory=list)


class AnalyticsService(ProgressObserver):
    """Service for analytics and reporting (FR6). Also acts as ProgressObserver."""

    def __init__(
        self,
        course_repo: CourseRepository,
        learner_repo: LearnerRepository,
        enrollment_repo: EnrollmentRepository,
        prerequisite_repo: PrerequisiteRepository,
        graph: PrerequisiteGraph,
    ) -> None:
        self._course_repo = course_repo
        self._learner_repo = learner_repo
        self._enrollment_repo = enrollment_repo
        self._prerequisite_repo = prerequisite_repo
        self._graph = graph
        self._cache_invalid = True
        self._cached_report: Optional[AnalyticsReport] = None

    def set_graph(self, graph: PrerequisiteGraph) -> None:
        self._graph = graph
        self._invalidate_cache()

    def _invalidate_cache(self) -> None:
        self._cache_invalid = True

    def on_enrollment_created(self, learner_id: str, course_code: str) -> None:
        self._invalidate_cache()
        logger.debug("Analytics cache invalidated: enrollment created")

    def on_enrollment_completed(
        self, learner_id: str, course_code: str, score: Optional[float]
    ) -> None:
        self._invalidate_cache()
        logger.debug("Analytics cache invalidated: enrollment completed")

    def on_course_updated(self, course_code: str) -> None:
        self._invalidate_cache()

    def get_system_metrics(self) -> SystemMetrics:
        courses = self._course_repo.list_all()
        learners = self._learner_repo.list_all()
        enrollments = self._enrollment_repo.list_all()
        completed = self._enrollment_repo.count_by_status(EnrollmentStatus.COMPLETED)
        published = len([c for c in courses if c.status.value == "published"])
        complexity = compute_graph_complexity(self._graph)

        total_enrollments = len(enrollments)
        completion_rate = (
            (completed / total_enrollments * 100) if total_enrollments > 0 else 0.0
        )

        return SystemMetrics(
            total_courses=len(courses),
            published_courses=published,
            total_learners=len(learners),
            total_enrollments=total_enrollments,
            completed_enrollments=completed,
            completion_rate=completion_rate,
            graph_depth=int(complexity["max_depth"]),
            graph_edges=int(complexity["edge_count"]),
            average_prerequisites=float(complexity["average_prerequisites"]),
        )

    def get_course_completion_stats(self) -> List[CourseCompletionStats]:
        stats: List[CourseCompletionStats] = []
        for course in self._course_repo.list_all():
            enrollments = self._enrollment_repo.list_by_course(course.code)
            completed = [
                e for e in enrollments if e.status == EnrollmentStatus.COMPLETED
            ]
            total = len(enrollments)
            rate = (len(completed) / total * 100) if total > 0 else 0.0
            scores = [e.score for e in completed if e.score is not None]
            avg_score = sum(scores) / len(scores) if scores else None
            stats.append(
                CourseCompletionStats(
                    course_code=course.code,
                    course_name=course.name,
                    total_enrollments=total,
                    completed_count=len(completed),
                    completion_rate=rate,
                    average_score=avg_score,
                )
            )
        return sorted(stats, key=lambda s: s.completion_rate)

    def get_bottleneck_courses(
        self, threshold: float = 0.5
    ) -> List[Tuple[str, int, float]]:
        completion_rates: Dict[str, float] = {}
        for stat in self.get_course_completion_stats():
            completion_rates[stat.course_code] = stat.completion_rate / 100.0
        return identify_bottleneck_courses(self._graph, completion_rates, threshold)

    def generate_report(self) -> AnalyticsReport:
        if not self._cache_invalid and self._cached_report:
            return self._cached_report

        report = AnalyticsReport(
            system_metrics=self.get_system_metrics(),
            course_stats=self.get_course_completion_stats(),
            bottlenecks=self.get_bottleneck_courses(),
        )
        self._cached_report = report
        self._cache_invalid = False
        return report

    def get_prerequisite_complexity(self) -> Dict[str, int | float]:
        return compute_graph_complexity(self._graph)
