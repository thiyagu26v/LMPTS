"""Unit tests for design patterns."""

import pytest

from lmpts.core.algorithms import PrerequisiteGraph
from lmpts.core.exceptions import EntityValidationError
from lmpts.core.patterns import (
    CourseFactory,
    DifficultyProgressiveStrategy,
    EnrollmentFactory,
    LearnerFactory,
    LoggingObserver,
    MinimumDurationStrategy,
    Observable,
    PathFinder,
    ProgressObserver,
    ShortestPathStrategy,
)


class TestFactories:
    def test_course_factory_valid(self):
        course = CourseFactory.create(
            code="CS101",
            name="Intro",
            description="Test",
            difficulty="beginner",
            duration_hours=40.0,
        )
        assert course.code == "CS101"

    def test_course_factory_invalid(self):
        with pytest.raises(EntityValidationError):
            CourseFactory.create(
                code="",
                name="Intro",
                description="Test",
                difficulty="beginner",
                duration_hours=40.0,
            )

    def test_learner_factory(self):
        learner = LearnerFactory.create("L001", "Alice", "a@test.com")
        assert learner.learner_id == "L001"

    def test_enrollment_factory(self):
        enrollment = EnrollmentFactory.create("L001", "CS101")
        assert enrollment.course_code == "CS101"


class TestStrategyPattern:
    @pytest.fixture
    def graph(self):
        g = PrerequisiteGraph()
        g.add_edge("A", "B")
        g.add_edge("B", "C")
        return g

    def test_shortest_path_strategy(self, graph):
        finder = PathFinder(ShortestPathStrategy())
        path = finder.find_path(
            graph, "A", "C", {"A": 10, "B": 10, "C": 10}, {"A": 1, "B": 2, "C": 3}
        )
        assert path == ["A", "B", "C"]

    def test_difficulty_strategy(self, graph):
        finder = PathFinder(DifficultyProgressiveStrategy())
        path = finder.find_path(
            graph, "A", "C", {"A": 10, "B": 10, "C": 10}, {"A": 1, "B": 2, "C": 3}
        )
        assert path is not None
        assert path[0] == "A"
        assert path[-1] == "C"

    def test_minimum_duration_strategy(self, graph):
        finder = PathFinder(MinimumDurationStrategy())
        path = finder.find_path(
            graph, "A", "C", {"A": 5, "B": 20, "C": 5}, {"A": 1, "B": 2, "C": 3}
        )
        assert path is not None

    def test_strategy_swap(self, graph):
        finder = PathFinder()
        finder.set_strategy(ShortestPathStrategy())
        path1 = finder.find_path(graph, "A", "C", {}, {})
        finder.set_strategy(DifficultyProgressiveStrategy())
        path2 = finder.find_path(
            graph, "A", "C", {"A": 1, "B": 1, "C": 1}, {"A": 1, "B": 2, "C": 3}
        )
        assert path1 is not None
        assert path2 is not None


class TestObserverPattern:
    class MockObserver(ProgressObserver):
        def __init__(self):
            self.events = []

        def on_enrollment_created(self, learner_id, course_code):
            self.events.append(("created", learner_id, course_code))

        def on_enrollment_completed(self, learner_id, course_code, score):
            self.events.append(("completed", learner_id, course_code, score))

        def on_course_updated(self, course_code):
            self.events.append(("updated", course_code))

    def test_observer_notification(self):
        obs = Observable()
        mock = self.MockObserver()
        obs.register_observer(mock)
        obs.notify_enrollment_created("L001", "CS101")
        assert len(mock.events) == 1
        obs.notify_enrollment_completed("L001", "CS101", 90.0)
        assert len(mock.events) == 2

    def test_logging_observer(self):
        messages = []
        observer = LoggingObserver(messages.append)
        observer.on_enrollment_created("L001", "CS101")
        assert "Enrollment created" in messages[0]
