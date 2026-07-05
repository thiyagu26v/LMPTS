"""Application bootstrap and dependency wiring."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from lmpts.core.algorithms import PrerequisiteGraph
from lmpts.data.database import DatabaseManager
from lmpts.data.repository import (
    CourseRepository,
    EnrollmentRepository,
    LearnerRepository,
    PrerequisiteRepository,
)
from lmpts.services.analytics_service import AnalyticsService
from lmpts.services.course_service import CourseService
from lmpts.services.enrollment_service import EnrollmentService
from lmpts.services.learner_service import LearnerService
from lmpts.services.learning_path_service import LearningPathService

logger = logging.getLogger(__name__)


class ServiceContainer:
    """Dependency injection container for all services."""

    def __init__(self, db_path: Optional[Path] = None) -> None:
        self.db = DatabaseManager(db_path)
        self.db.initialize()

        self.course_repo = CourseRepository(self.db)
        self.learner_repo = LearnerRepository(self.db)
        self.enrollment_repo = EnrollmentRepository(self.db)
        self.prerequisite_repo = PrerequisiteRepository(self.db)

        self.graph = self._build_graph()

        self.course_service = CourseService(
            self.course_repo, self.prerequisite_repo, self.graph
        )
        self.learner_service = LearnerService(self.learner_repo)
        self.learner_service.set_enrollment_repo(self.enrollment_repo)
        self.enrollment_service = EnrollmentService(
            self.course_repo,
            self.learner_repo,
            self.enrollment_repo,
            self.graph,
        )
        self.learning_path_service = LearningPathService(
            self.course_repo, self.prerequisite_repo, self.graph
        )
        self.analytics_service = AnalyticsService(
            self.course_repo,
            self.learner_repo,
            self.enrollment_repo,
            self.prerequisite_repo,
            self.graph,
        )

        self.enrollment_service.register_observer(self.analytics_service)

    def _build_graph(self) -> PrerequisiteGraph:
        graph = PrerequisiteGraph()
        edges = self.prerequisite_repo.get_all_edges()
        for course in self.course_repo.list_all():
            graph.add_node(course.code)
        for prereq, dep in edges:
            try:
                graph.add_edge(prereq, dep)
            except Exception:
                logger.warning("Skipping invalid edge %s -> %s", prereq, dep)
        return graph

    def refresh_graph(self) -> None:
        """Rebuild graph after prerequisite changes."""
        self.graph = self._build_graph()
        self.course_service.set_graph(self.graph)
        self.enrollment_service.set_graph(self.graph)
        self.learning_path_service.set_graph(self.graph)
        self.analytics_service.set_graph(self.graph)
