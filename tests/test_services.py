"""Tests for service layer."""

import pytest

from lmpts.core.enums import CourseStatus
from lmpts.core.exceptions import (
    CircularDependencyError,
    CourseNotFoundError,
    EnrollmentError,
    LearnerNotFoundError,
    PrerequisiteNotMetError,
    ValidationError,
)


class TestCourseService:
    def test_create_course(self, container, sample_course_data):
        course = container.course_service.create_course(**sample_course_data)
        assert course.code == "TEST101"

    def test_duplicate_course_raises(self, container, sample_course_data):
        container.course_service.create_course(**sample_course_data)
        with pytest.raises(ValidationError):
            container.course_service.create_course(**sample_course_data)

    def test_add_prerequisite_with_cycle(self, container):
        with pytest.raises(CircularDependencyError):
            container.course_service.add_prerequisite("CS102", "CS101")

    def test_transitive_prerequisites(self, container):
        transitive = container.course_service.get_transitive_prerequisites("CS301")
        assert "CS101" in transitive

    def test_delete_course_cascades(self, container, sample_course_data):
        container.course_service.create_course(**sample_course_data)
        container.course_service.publish_course("TEST101")
        container.course_service.delete_course("TEST101")
        with pytest.raises(CourseNotFoundError):
            container.course_service.get_course("TEST101")


class TestLearnerService:
    def test_register_learner(self, container):
        learner = container.learner_service.register_learner(
            "NEW001", "New Learner", "new@test.com"
        )
        assert learner.learner_id == "NEW001"

    def test_duplicate_learner(self, container):
        with pytest.raises(ValidationError):
            container.learner_service.register_learner(
                "L001", "Duplicate", "dup@test.com"
            )

    def test_get_progress(self, container):
        progress = container.learner_service.get_progress("L001")
        assert progress.learner_id == "L001"
        assert progress.total_enrollments >= 0


class TestEnrollmentService:
    def test_enroll_without_prerequisites_fails(self, container):
        with pytest.raises(PrerequisiteNotMetError):
            container.enrollment_service.enroll("L002", "CS301")

    def test_enroll_with_prerequisites(self, container):
        # L002 already completed CS101 in seed data
        enrollment = container.enrollment_service.enroll("L002", "CS102")
        assert enrollment.course_code == "CS102"

    def test_duplicate_enrollment(self, container):
        with pytest.raises(EnrollmentError):
            container.enrollment_service.enroll("L001", "CS101")

    def test_suggest_available_courses(self, container):
        suggested = container.enrollment_service.suggest_available_courses("L001")
        assert isinstance(suggested, set)

    def test_validate_enrollment(self, container):
        ok, msg = container.enrollment_service.validate_enrollment("L001", "CS301")
        assert not ok


class TestLearningPathService:
    def test_shortest_path(self, container):
        path, stats = container.learning_path_service.find_shortest_path("CS101", "CS301")
        assert path is not None
        assert path[0] == "CS101"
        assert path[-1] == "CS301"
        assert stats is not None
        assert stats.total_hours > 0

    def test_multiple_strategies(self, container):
        paths = container.learning_path_service.find_multiple_paths("CS101", "CS301")
        assert len(paths) >= 1

    def test_validate_path(self, container):
        path, _ = container.learning_path_service.find_shortest_path("CS101", "CS301")
        valid, msg = container.learning_path_service.validate_path(path)
        assert valid

    def test_invalid_strategy(self, container):
        with pytest.raises(ValidationError):
            container.learning_path_service.find_path_with_strategy(
                "CS101", "CS301", "invalid"
            )


class TestAnalyticsService:
    def test_system_metrics(self, container):
        metrics = container.analytics_service.get_system_metrics()
        assert metrics.total_courses > 0
        assert metrics.total_learners > 0

    def test_course_completion_stats(self, container):
        stats = container.analytics_service.get_course_completion_stats()
        assert len(stats) > 0

    def test_generate_report(self, container):
        report = container.analytics_service.generate_report()
        assert report.system_metrics.total_courses > 0

    def test_bottleneck_detection(self, container):
        bottlenecks = container.analytics_service.get_bottleneck_courses()
        assert isinstance(bottlenecks, list)
