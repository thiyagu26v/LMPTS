"""Enrollment and validation business logic."""

from __future__ import annotations

import logging
from typing import List, Optional, Set

from lmpts.core.algorithms import PrerequisiteGraph, recommend_available_courses
from lmpts.core.enums import CourseStatus, EnrollmentStatus
from lmpts.core.exceptions import (
    CourseNotFoundError,
    EnrollmentError,
    LearnerNotFoundError,
    PrerequisiteNotMetError,
    ValidationError,
)
from lmpts.core.models import Enrollment
from lmpts.core.patterns import EnrollmentFactory, Observable
from lmpts.data.repository import (
    CourseRepository,
    EnrollmentRepository,
    LearnerRepository,
)

logger = logging.getLogger(__name__)


class EnrollmentService(Observable):
    """Service for enrollment management and validation (FR4)."""

    def __init__(
        self,
        course_repo: CourseRepository,
        learner_repo: LearnerRepository,
        enrollment_repo: EnrollmentRepository,
        graph: PrerequisiteGraph,
    ) -> None:
        Observable.__init__(self)
        self._course_repo = course_repo
        self._learner_repo = learner_repo
        self._enrollment_repo = enrollment_repo
        self._graph = graph

    def set_graph(self, graph: PrerequisiteGraph) -> None:
        self._graph = graph

    def enroll(self, learner_id: str, course_code: str) -> Enrollment:
        """Enroll learner with full prerequisite validation."""
        learner_id = learner_id.strip()
        code = course_code.strip().upper()

        if not self._learner_repo.exists(learner_id):
            raise LearnerNotFoundError(f"Learner {learner_id} not found")

        course = self._course_repo.read(code)
        if not course:
            raise CourseNotFoundError(f"Course {code} not found")

        if course.status == CourseStatus.ARCHIVED:
            raise EnrollmentError(f"Cannot enroll in archived course {code}")

        if course.status != CourseStatus.PUBLISHED:
            raise EnrollmentError(
                f"Course {code} is not published (status: {course.status.value})"
            )

        existing = self._enrollment_repo.find_by_learner_and_course(learner_id, code)
        if existing and existing.status != EnrollmentStatus.DROPPED:
            raise EnrollmentError(
                f"Learner {learner_id} is already enrolled in {code}"
            )

        self._validate_prerequisites(learner_id, code)

        enrollment = EnrollmentFactory.create(learner_id=learner_id, course_code=code)
        saved = self._enrollment_repo.create(enrollment)
        self.notify_enrollment_created(learner_id, code)
        logger.info("Enrolled %s in %s", learner_id, code)
        return saved

    def _validate_prerequisites(self, learner_id: str, course_code: str) -> None:
        """Validate all transitive prerequisites are completed."""
        required = self._graph.get_transitive_prerequisites(course_code)
        if not required:
            return

        completed = self._get_completed_courses(learner_id)
        missing = required - completed
        if missing:
            missing_list = ", ".join(sorted(missing))
            raise PrerequisiteNotMetError(
                f"Missing prerequisites for {course_code}: {missing_list}"
            )

    def _get_completed_courses(self, learner_id: str) -> Set[str]:
        enrollments = self._enrollment_repo.list_completed_by_learner(learner_id)
        return {e.course_code for e in enrollments}

    def complete_course(
        self, learner_id: str, course_code: str, score: Optional[float] = None
    ) -> Enrollment:
        enrollment = self._enrollment_repo.find_by_learner_and_course(
            learner_id, course_code
        )
        if not enrollment:
            raise EnrollmentError(
                f"Learner {learner_id} is not enrolled in {course_code}"
            )
        if enrollment.status == EnrollmentStatus.COMPLETED:
            raise EnrollmentError(f"Course {course_code} already completed")

        enrollment.mark_completed(score)
        updated = self._enrollment_repo.update(enrollment)
        self.notify_enrollment_completed(learner_id, course_code, score)
        logger.info("Completed %s for %s (score=%s)", course_code, learner_id, score)
        return updated

    def drop_enrollment(self, learner_id: str, course_code: str) -> Enrollment:
        enrollment = self._enrollment_repo.find_by_learner_and_course(
            learner_id, course_code
        )
        if not enrollment:
            raise EnrollmentError(
                f"Learner {learner_id} is not enrolled in {course_code}"
            )
        enrollment.status = EnrollmentStatus.DROPPED
        return self._enrollment_repo.update(enrollment)

    def get_enrollments_for_learner(self, learner_id: str) -> List[Enrollment]:
        if not self._learner_repo.exists(learner_id):
            raise LearnerNotFoundError(f"Learner {learner_id} not found")
        return self._enrollment_repo.list_by_learner(learner_id)

    def suggest_available_courses(self, learner_id: str) -> Set[str]:
        """Suggest courses the learner can enroll in based on completed prerequisites."""
        if not self._learner_repo.exists(learner_id):
            raise LearnerNotFoundError(f"Learner {learner_id} not found")

        completed = self._get_completed_courses(learner_id)
        enrolled = {
            e.course_code
            for e in self._enrollment_repo.list_by_learner(learner_id)
            if e.status != EnrollmentStatus.DROPPED
        }
        published = {
            c.code for c in self._course_repo.list_by_status(CourseStatus.PUBLISHED)
        }
        all_courses = published - enrolled
        return recommend_available_courses(
            all_courses, completed, self._graph, published
        )

    def validate_enrollment(self, learner_id: str, course_code: str) -> tuple[bool, str]:
        """Check if enrollment would succeed without persisting."""
        try:
            learner_id = learner_id.strip()
            code = course_code.strip().upper()
            if not self._learner_repo.exists(learner_id):
                return False, f"Learner {learner_id} not found"
            course = self._course_repo.read(code)
            if not course:
                return False, f"Course {code} not found"
            if course.status != CourseStatus.PUBLISHED:
                return False, f"Course {code} is not published"
            existing = self._enrollment_repo.find_by_learner_and_course(
                learner_id, code
            )
            if existing and existing.status != EnrollmentStatus.DROPPED:
                return False, f"Already enrolled in {code}"
            self._validate_prerequisites(learner_id, code)
            return True, "Enrollment valid"
        except PrerequisiteNotMetError as exc:
            return False, exc.message
        except EnrollmentError as exc:
            return False, exc.message
