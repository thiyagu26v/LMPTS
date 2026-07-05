"""GUI controllers connecting views to services."""

from __future__ import annotations

import logging
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable, Optional

from lmpts.core.exceptions import LMPTSError
from lmpts.core.patterns import GUIRefreshObserver
from lmpts.services.container import ServiceContainer

logger = logging.getLogger(__name__)


class BaseController:
    """Base controller with error handling."""

    def __init__(self, container: ServiceContainer) -> None:
        self.container = container

    def handle_error(self, exc: Exception) -> str:
        if isinstance(exc, LMPTSError):
            message = exc.message
        else:
            message = str(exc)
        logger.error("Operation failed: %s", message)
        return message


class AdminController(BaseController):
    """Controller for admin course and prerequisite management."""

    def create_course(self, data: dict) -> tuple[bool, str]:
        try:
            self.container.course_service.create_course(**data)
            self.container.refresh_graph()
            return True, f"Course {data['code']} created successfully"
        except Exception as exc:
            return False, self.handle_error(exc)

    def update_course(self, code: str, data: dict) -> tuple[bool, str]:
        try:
            self.container.course_service.update_course(code, **data)
            return True, f"Course {code} updated"
        except Exception as exc:
            return False, self.handle_error(exc)

    def delete_course(self, code: str) -> tuple[bool, str]:
        try:
            if messagebox.askyesno("Confirm Delete", f"Delete course {code}?"):
                self.container.course_service.delete_course(code)
                self.container.refresh_graph()
                return True, f"Course {code} deleted"
            return False, "Cancelled"
        except Exception as exc:
            return False, self.handle_error(exc)

    def add_prerequisite(self, prereq: str, dependent: str) -> tuple[bool, str]:
        try:
            self.container.course_service.add_prerequisite(prereq, dependent)
            self.container.refresh_graph()
            return True, f"Added prerequisite {prereq} -> {dependent}"
        except Exception as exc:
            return False, self.handle_error(exc)

    def remove_prerequisite(self, prereq: str, dependent: str) -> tuple[bool, str]:
        try:
            self.container.course_service.remove_prerequisite(prereq, dependent)
            self.container.refresh_graph()
            return True, f"Removed prerequisite {prereq} -> {dependent}"
        except Exception as exc:
            return False, self.handle_error(exc)

    def list_courses(self) -> list:
        return self.container.course_service.list_courses()

    def get_prerequisites(self, code: str) -> set:
        try:
            direct = self.container.course_service.get_direct_prerequisites(code)
            transitive = self.container.course_service.get_transitive_prerequisites(code)
            return direct, transitive
        except Exception:
            return set(), set()

    def publish_course(self, code: str) -> tuple[bool, str]:
        try:
            self.container.course_service.publish_course(code)
            return True, f"Course {code} published"
        except Exception as exc:
            return False, self.handle_error(exc)


class LearnerController(BaseController):
    """Controller for learner portal."""

    def __init__(self, container: ServiceContainer, refresh_callback: Callable) -> None:
        super().__init__(container)
        observer = GUIRefreshObserver(refresh_callback)
        container.enrollment_service.register_observer(observer)

    def register_learner(self, learner_id: str, name: str, email: str) -> tuple[bool, str]:
        try:
            self.container.learner_service.register_learner(learner_id, name, email)
            return True, f"Learner {learner_id} registered"
        except Exception as exc:
            return False, self.handle_error(exc)

    def enroll(self, learner_id: str, course_code: str) -> tuple[bool, str]:
        try:
            self.container.enrollment_service.enroll(learner_id, course_code)
            return True, f"Enrolled in {course_code}"
        except Exception as exc:
            return False, self.handle_error(exc)

    def complete_course(
        self, learner_id: str, course_code: str, score: Optional[float]
    ) -> tuple[bool, str]:
        try:
            self.container.enrollment_service.complete_course(
                learner_id, course_code, score
            )
            return True, f"Completed {course_code}"
        except Exception as exc:
            return False, self.handle_error(exc)

    def validate_enrollment(self, learner_id: str, course_code: str) -> tuple[bool, str]:
        return self.container.enrollment_service.validate_enrollment(
            learner_id, course_code
        )

    def get_progress(self, learner_id: str):
        try:
            return self.container.learner_service.get_progress(learner_id)
        except Exception as exc:
            self.handle_error(exc)
            return None

    def suggest_courses(self, learner_id: str) -> set:
        try:
            return self.container.enrollment_service.suggest_available_courses(learner_id)
        except Exception:
            return set()

    def list_learners(self) -> list:
        return self.container.learner_service.list_learners()

    def get_enrollments(self, learner_id: str) -> list:
        try:
            return self.container.enrollment_service.get_enrollments_for_learner(
                learner_id
            )
        except Exception:
            return []


class AnalyticsController(BaseController):
    """Controller for analytics dashboard."""

    def get_report(self):
        return self.container.analytics_service.generate_report()

    def get_system_metrics(self):
        return self.container.analytics_service.get_system_metrics()


class PathController(BaseController):
    """Controller for learning path computation."""

    def find_path(self, start: str, target: str, strategy: str = "shortest"):
        try:
            return self.container.learning_path_service.find_path_with_strategy(
                start, target, strategy
            )
        except Exception as exc:
            self.handle_error(exc)
            return None, None

    def find_multiple_paths(self, start: str, target: str):
        try:
            return self.container.learning_path_service.find_multiple_paths(start, target)
        except Exception as exc:
            self.handle_error(exc)
            return []

    def get_strategies(self) -> list:
        return self.container.learning_path_service.get_available_strategies()

    def validate_path(self, path: list) -> tuple[bool, str]:
        return self.container.learning_path_service.validate_path(path)
