"""Edge case and regression tests."""

import pytest

from lmpts.core.algorithms import PrerequisiteGraph
from lmpts.core.exceptions import (
    CircularDependencyError,
    CourseNotFoundError,
    EntityValidationError,
    ValidationError,
)
from lmpts.core.patterns import CourseFactory


class TestEdgeCases:
    def test_empty_prerequisites_set(self):
        course = CourseFactory.create(
            code="EDGE1", name="Edge", description="", difficulty="beginner", duration_hours=10
        )
        assert course.prerequisites == set()

    def test_empty_graph_path(self):
        g = PrerequisiteGraph()
        assert g.shortest_path("A", "B") is None

    def test_single_node_graph(self):
        g = PrerequisiteGraph()
        g.add_node("SOLO")
        assert g.shortest_path("SOLO", "SOLO") == ["SOLO"]

    def test_zero_duration_rejected(self):
        with pytest.raises(EntityValidationError):
            CourseFactory.create(
                code="ZERO", name="Zero", description="", difficulty="beginner", duration_hours=0
            )

    def test_enroll_archived_course(self, container):
        container.course_service.create_course(
            code="ARCH1", name="Archived", description="", difficulty="beginner", duration_hours=10
        )
        container.course_service.archive_course("ARCH1")
        learner = container.learner_service.register_learner(
            "EDGE_L", "Edge Learner", "edge@test.com"
        )
        from lmpts.core.exceptions import EnrollmentError

        with pytest.raises(EnrollmentError):
            container.enrollment_service.enroll(learner.learner_id, "ARCH1")

    def test_nonexistent_course_enrollment(self, container):
        from lmpts.core.exceptions import CourseNotFoundError

        with pytest.raises(CourseNotFoundError):
            container.enrollment_service.enroll("L001", "NONEXIST")

    def test_nonexistent_learner_enrollment(self, container):
        from lmpts.core.exceptions import LearnerNotFoundError

        with pytest.raises(LearnerNotFoundError):
            container.enrollment_service.enroll("NONEXIST", "CS101")

    def test_duplicate_prerequisite(self, container):
        with pytest.raises(ValidationError):
            container.course_service.add_prerequisite("CS101", "CS102")

    def test_path_validation_empty(self, container):
        valid, msg = container.learning_path_service.validate_path([])
        assert not valid

    def test_path_validation_duplicates(self, container):
        valid, msg = container.learning_path_service.validate_path(["CS101", "CS101"])
        assert not valid

    def test_invalid_difficulty_enum(self):
        with pytest.raises(ValueError):
            from lmpts.core.enums import DifficultyLevel

            DifficultyLevel.from_string("impossible")

    def test_delete_nonexistent_course(self, container):
        with pytest.raises(CourseNotFoundError):
            container.course_service.delete_course("GHOST")

    def test_large_graph_performance(self):
        """Basic performance test: 100 node chain."""
        g = PrerequisiteGraph()
        for i in range(99):
            g.add_edge(f"C{i:03d}", f"C{i+1:03d}")
        path = g.shortest_path("C000", "C099")
        assert path is not None
        assert len(path) == 100

    def test_cycle_in_existing_graph(self):
        g = PrerequisiteGraph()
        g.add_edge("X", "Y")
        g.add_edge("Y", "Z")
        with pytest.raises(CircularDependencyError):
            g.add_edge("Z", "X")
