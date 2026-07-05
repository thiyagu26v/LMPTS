"""Integration tests for complete workflows."""

import pytest

from lmpts.core.exceptions import CircularDependencyError, PrerequisiteNotMetError


class TestEnrollmentWorkflow:
    """Integration: complete prerequisite chain enrollment."""

    def test_full_enrollment_workflow(self, container):
        learner = container.learner_service.register_learner(
            "INT001", "Integration User", "int@test.com"
        )

        ok, msg = container.enrollment_service.validate_enrollment(
            learner.learner_id, "CS101"
        )
        assert ok

        container.enrollment_service.enroll(learner.learner_id, "CS101")
        container.enrollment_service.complete_course(learner.learner_id, "CS101", 95.0)

        ok, msg = container.enrollment_service.validate_enrollment(
            learner.learner_id, "CS102"
        )
        assert ok

        container.enrollment_service.enroll(learner.learner_id, "CS102")
        progress = container.learner_service.get_progress(learner.learner_id)
        assert progress.completed_count >= 1

    def test_prerequisite_chain_blocks_enrollment(self, container):
        learner = container.learner_service.register_learner(
            "INT002", "Blocked User", "blocked@test.com"
        )
        with pytest.raises(PrerequisiteNotMetError):
            container.enrollment_service.enroll(learner.learner_id, "CS301")


class TestCoursePrerequisiteWorkflow:
    """Integration: course and prerequisite management."""

    def test_create_courses_and_prerequisites(self, container):
        container.course_service.create_course(
            code="INTA",
            name="Course A",
            description="A",
            difficulty="beginner",
            duration_hours=10,
        )
        container.course_service.create_course(
            code="INTB",
            name="Course B",
            description="B",
            difficulty="beginner",
            duration_hours=10,
        )
        container.course_service.publish_course("INTA")
        container.course_service.publish_course("INTB")
        container.course_service.add_prerequisite("INTA", "INTB")
        container.refresh_graph()

        direct = container.course_service.get_direct_prerequisites("INTB")
        assert "INTA" in direct

    def test_cycle_prevention(self, container):
        container.course_service.create_course(
            code="CYCA", name="A", description="", difficulty="beginner", duration_hours=10
        )
        container.course_service.create_course(
            code="CYCB", name="B", description="", difficulty="beginner", duration_hours=10
        )
        container.course_service.create_course(
            code="CYCC", name="C", description="", difficulty="beginner", duration_hours=10
        )
        container.course_service.add_prerequisite("CYCA", "CYCB")
        container.course_service.add_prerequisite("CYCB", "CYCC")
        container.refresh_graph()

        with pytest.raises(CircularDependencyError):
            container.course_service.add_prerequisite("CYCC", "CYCA")


class TestLearningPathWorkflow:
    """Integration: learning path computation."""

    def test_path_from_beginner_to_advanced(self, container):
        path, stats = container.learning_path_service.find_shortest_path(
            "CS101", "CS301"
        )
        assert path is not None
        valid, _ = container.learning_path_service.validate_path(path)
        assert valid
        assert stats.course_count == len(path)


class TestAnalyticsWorkflow:
    """Integration: analytics after enrollments."""

    def test_analytics_reflects_enrollments(self, container):
        initial = container.analytics_service.get_system_metrics()
        learner = container.learner_service.register_learner(
            "ANA001", "Analyst Test", "ana@test.com"
        )
        container.enrollment_service.enroll(learner.learner_id, "CS101")
        updated = container.analytics_service.get_system_metrics()
        assert updated.total_enrollments >= initial.total_enrollments
