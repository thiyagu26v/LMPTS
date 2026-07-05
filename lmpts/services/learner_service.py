"""Learner management business logic."""

from __future__ import annotations

import logging
from typing import List, Set

from lmpts.core.enums import EnrollmentStatus
from lmpts.core.exceptions import LearnerNotFoundError, ValidationError
from lmpts.core.models import Learner, LearnerProgress
from lmpts.core.patterns import LearnerFactory
from lmpts.data.repository import EnrollmentRepository, LearnerRepository

logger = logging.getLogger(__name__)


class LearnerService:
    """Service for learner profile management (FR3)."""

    def __init__(
        self,
        learner_repo: LearnerRepository,
        enrollment_repo: EnrollmentRepository | None = None,
    ) -> None:
        self._learner_repo = learner_repo
        self._enrollment_repo = enrollment_repo

    def set_enrollment_repo(self, enrollment_repo: EnrollmentRepository) -> None:
        self._enrollment_repo = enrollment_repo

    def register_learner(self, learner_id: str, name: str, email: str) -> Learner:
        if self._learner_repo.exists(learner_id):
            raise ValidationError(f"Learner {learner_id.strip()} already exists")
        learner = LearnerFactory.create(
            learner_id=learner_id, name=name, email=email
        )
        saved = self._learner_repo.create(learner)
        logger.info("Registered learner %s", saved.learner_id)
        return saved

    def get_learner(self, learner_id: str) -> Learner:
        learner = self._learner_repo.read(learner_id)
        if not learner:
            raise LearnerNotFoundError(f"Learner {learner_id.strip()} not found")
        return learner

    def update_learner(
        self, learner_id: str, name: str | None = None, email: str | None = None
    ) -> Learner:
        learner = self.get_learner(learner_id)
        if name is not None:
            learner.name = name
        if email is not None:
            learner.email = email
        is_valid, message = learner.validate()
        if not is_valid:
            raise ValidationError(message)
        return self._learner_repo.update(learner)

    def delete_learner(self, learner_id: str) -> bool:
        if not self._learner_repo.exists(learner_id):
            raise LearnerNotFoundError(f"Learner {learner_id.strip()} not found")
        return self._learner_repo.delete(learner_id)

    def list_learners(self) -> List[Learner]:
        return self._learner_repo.list_all()

    def get_enrollment_history(self, learner_id: str) -> list:
        self.get_learner(learner_id)
        if not self._enrollment_repo:
            return []
        return self._enrollment_repo.list_by_learner(learner_id)

    def get_completed_courses(self, learner_id: str) -> Set[str]:
        self.get_learner(learner_id)
        if not self._enrollment_repo:
            return set()
        enrollments = self._enrollment_repo.list_completed_by_learner(learner_id)
        return {e.course_code for e in enrollments}

    def get_progress(self, learner_id: str) -> LearnerProgress:
        self.get_learner(learner_id)
        if not self._enrollment_repo:
            return LearnerProgress(
                learner_id=learner_id,
                total_enrollments=0,
                completed_count=0,
                in_progress_count=0,
                completion_rate=0.0,
                completed_courses=[],
                in_progress_courses=[],
            )
        enrollments = self._enrollment_repo.list_by_learner(learner_id)
        completed = [
            e.course_code
            for e in enrollments
            if e.status == EnrollmentStatus.COMPLETED
        ]
        in_progress = [
            e.course_code
            for e in enrollments
            if e.status in (EnrollmentStatus.ENROLLED, EnrollmentStatus.IN_PROGRESS)
        ]
        total = len(enrollments)
        completed_count = len(completed)
        rate = (completed_count / total * 100) if total > 0 else 0.0
        return LearnerProgress(
            learner_id=learner_id,
            total_enrollments=total,
            completed_count=completed_count,
            in_progress_count=len(in_progress),
            completion_rate=rate,
            completed_courses=completed,
            in_progress_courses=in_progress,
        )
