"""Course management business logic."""

from __future__ import annotations

import logging
from typing import List, Optional, Set

from lmpts.core.algorithms import PrerequisiteGraph
from lmpts.core.enums import CourseStatus, DifficultyLevel
from lmpts.core.exceptions import (
    CircularDependencyError,
    CourseNotFoundError,
    EntityValidationError,
    ValidationError,
)
from lmpts.core.models import Course, PrerequisiteRelation
from lmpts.core.patterns import CourseFactory, Observable
from lmpts.data.repository import CourseRepository, PrerequisiteRepository

logger = logging.getLogger(__name__)


class CourseService(Observable):
    """Service for course and prerequisite management (FR1, FR2)."""

    def __init__(
        self,
        course_repo: CourseRepository,
        prerequisite_repo: PrerequisiteRepository,
        graph: PrerequisiteGraph,
    ) -> None:
        Observable.__init__(self)
        self._course_repo = course_repo
        self._prerequisite_repo = prerequisite_repo
        self._graph = graph

    def set_graph(self, graph: PrerequisiteGraph) -> None:
        self._graph = graph

    def create_course(
        self,
        code: str,
        name: str,
        description: str,
        difficulty: DifficultyLevel | str,
        duration_hours: float,
        instructor: str = "",
        status: CourseStatus | str = CourseStatus.DRAFT,
    ) -> Course:
        """Create a new course with validation."""
        if self._course_repo.exists(code):
            raise ValidationError(f"Course {code.strip().upper()} already exists")
        course = CourseFactory.create(
            code=code,
            name=name,
            description=description,
            difficulty=difficulty,
            duration_hours=duration_hours,
            instructor=instructor,
            status=status,
        )
        saved = self._course_repo.create(course)
        self._graph.add_node(saved.code)
        logger.info("Created course %s", saved.code)
        return saved

    def get_course(self, code: str) -> Course:
        course = self._course_repo.read(code)
        if not course:
            raise CourseNotFoundError(f"Course {code.strip().upper()} not found")
        return course

    def update_course(
        self,
        code: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        difficulty: Optional[DifficultyLevel | str] = None,
        duration_hours: Optional[float] = None,
        instructor: Optional[str] = None,
        status: Optional[CourseStatus | str] = None,
    ) -> Course:
        course = self.get_course(code)
        if name is not None:
            course.name = name
        if description is not None:
            course.description = description
        if difficulty is not None:
            course.difficulty = (
                DifficultyLevel.from_string(difficulty)
                if isinstance(difficulty, str)
                else difficulty
            )
        if duration_hours is not None:
            if duration_hours <= 0:
                raise ValidationError("Duration must be greater than zero")
            course.duration_hours = duration_hours
        if instructor is not None:
            course.instructor = instructor
        if status is not None:
            course.status = (
                CourseStatus.from_string(status)
                if isinstance(status, str)
                else status
            )
        is_valid, message = course.validate()
        if not is_valid:
            raise EntityValidationError(message)
        updated = self._course_repo.update(course)
        self.notify_course_updated(updated.code)
        return updated

    def delete_course(self, code: str) -> bool:
        course_code = code.strip().upper()
        if not self._course_repo.exists(course_code):
            raise CourseNotFoundError(f"Course {course_code} not found")
        result = self._course_repo.delete(course_code)
        if result:
            self._graph = PrerequisiteGraph()
            for edge in self._prerequisite_repo.get_all_edges():
                try:
                    self._graph.add_edge(edge[0], edge[1])
                except CircularDependencyError:
                    pass
            for c in self._course_repo.list_all():
                self._graph.add_node(c.code)
        return result

    def list_courses(self, status: Optional[CourseStatus] = None) -> List[Course]:
        if status:
            return self._course_repo.list_by_status(status)
        return self._course_repo.list_all()

    def search_courses(self, query: str) -> List[Course]:
        if not query.strip():
            return self.list_courses()
        return self._course_repo.search(query)

    def publish_course(self, code: str) -> Course:
        return self.update_course(code, status=CourseStatus.PUBLISHED)

    def archive_course(self, code: str) -> Course:
        return self.update_course(code, status=CourseStatus.ARCHIVED)

    def add_prerequisite(self, prerequisite_code: str, dependent_code: str) -> None:
        """Add prerequisite with cycle detection."""
        prereq = prerequisite_code.strip().upper()
        dep = dependent_code.strip().upper()
        if not self._course_repo.exists(prereq):
            raise CourseNotFoundError(f"Prerequisite course {prereq} not found")
        if not self._course_repo.exists(dep):
            raise CourseNotFoundError(f"Dependent course {dep} not found")
        if self._prerequisite_repo.exists(prereq, dep):
            raise ValidationError(
                f"Prerequisite {prereq} -> {dep} already exists"
            )
        try:
            self._graph.add_edge(prereq, dep)
        except CircularDependencyError as exc:
            raise CircularDependencyError(str(exc)) from exc
        relation = PrerequisiteRelation(prereq, dep)
        self._prerequisite_repo.add(relation)

    def remove_prerequisite(self, prerequisite_code: str, dependent_code: str) -> bool:
        prereq = prerequisite_code.strip().upper()
        dep = dependent_code.strip().upper()
        result = self._prerequisite_repo.remove(prereq, dep)
        if result:
            self._graph.remove_edge(prereq, dep)
        return result

    def get_direct_prerequisites(self, course_code: str) -> Set[str]:
        self.get_course(course_code)
        return self._graph.get_direct_prerequisites(course_code)

    def get_transitive_prerequisites(self, course_code: str) -> Set[str]:
        self.get_course(course_code)
        return self._graph.get_transitive_prerequisites(course_code)

    def get_course_levels(self) -> dict[str, int]:
        return self._graph.compute_course_levels()

    def detect_cycles(self) -> Optional[List[str]]:
        return self._graph.detect_cycle()

    def get_catalog(self) -> List[Course]:
        return self.list_courses(CourseStatus.PUBLISHED)
