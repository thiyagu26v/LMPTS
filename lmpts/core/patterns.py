"""Design pattern implementations for LMPTS."""

from abc import ABC, abstractmethod
from typing import Callable, Generic, List, Optional, Protocol, TypeVar

from lmpts.core.algorithms import PrerequisiteGraph, compute_path_statistics
from lmpts.core.enums import CourseStatus, DifficultyLevel
from lmpts.core.exceptions import EntityValidationError
from lmpts.core.models import Course, Enrollment, Learner, PathStatistics

T = TypeVar("T")


class Repository(ABC, Generic[T]):
    """Abstract repository contract (Repository Pattern)."""

    @abstractmethod
    def create(self, entity: T) -> T:
        """Persist a new entity."""

    @abstractmethod
    def read(self, entity_id: str) -> Optional[T]:
        """Retrieve entity by ID."""

    @abstractmethod
    def update(self, entity: T) -> T:
        """Update existing entity."""

    @abstractmethod
    def delete(self, entity_id: str) -> bool:
        """Delete entity by ID."""

    @abstractmethod
    def list_all(self) -> List[T]:
        """List all entities."""


class EntityFactory(ABC, Generic[T]):
    """Abstract factory for domain entity creation (Factory Pattern)."""

    @abstractmethod
    def create(self, **kwargs) -> T:
        """Create and validate entity."""


class CourseFactory(EntityFactory[Course]):
    """Factory for Course creation with centralized validation."""

    @staticmethod
    def create(
        code: str,
        name: str,
        description: str,
        difficulty: DifficultyLevel | str,
        duration_hours: float,
        instructor: str = "",
        status: CourseStatus | str = CourseStatus.DRAFT,
    ) -> Course:
        if isinstance(difficulty, str):
            difficulty = DifficultyLevel.from_string(difficulty)
        if isinstance(status, str):
            status = CourseStatus.from_string(status)

        course = Course(
            code=code,
            name=name,
            description=description,
            difficulty=difficulty,
            duration_hours=duration_hours,
            instructor=instructor,
            status=status,
        )
        is_valid, message = course.validate()
        if not is_valid:
            raise EntityValidationError(message)
        return course


class LearnerFactory(EntityFactory[Learner]):
    """Factory for Learner creation with validation."""

    @staticmethod
    def create(learner_id: str, name: str, email: str) -> Learner:
        learner = Learner(learner_id=learner_id, name=name, email=email)
        is_valid, message = learner.validate()
        if not is_valid:
            raise EntityValidationError(message)
        return learner


class EnrollmentFactory(EntityFactory[Enrollment]):
    """Factory for Enrollment creation with validation."""

    @staticmethod
    def create(
        learner_id: str,
        course_code: str,
        enrollment_id: Optional[int] = None,
    ) -> Enrollment:
        enrollment = Enrollment(
            enrollment_id=enrollment_id,
            learner_id=learner_id,
            course_code=course_code,
        )
        is_valid, message = enrollment.validate()
        if not is_valid:
            raise EntityValidationError(message)
        return enrollment


class PathFindingStrategy(ABC):
    """Strategy interface for learning path algorithms (Strategy Pattern)."""

    @abstractmethod
    def find_path(
        self,
        graph: PrerequisiteGraph,
        start: str,
        target: str,
        course_durations: dict[str, float],
        course_difficulties: dict[str, int],
    ) -> Optional[list[str]]:
        """Find a learning path using the strategy."""


class ShortestPathStrategy(PathFindingStrategy):
    """BFS-based shortest path strategy. O(V + E)."""

    def find_path(
        self,
        graph: PrerequisiteGraph,
        start: str,
        target: str,
        course_durations: dict[str, float],
        course_difficulties: dict[str, int],
    ) -> Optional[list[str]]:
        return graph.shortest_path(start, target)


class DifficultyProgressiveStrategy(PathFindingStrategy):
    """
    Path strategy favoring gradual difficulty increase.

    Uses topological sort filtered to reachable nodes, then orders by difficulty.
    """

    def find_path(
        self,
        graph: PrerequisiteGraph,
        start: str,
        target: str,
        course_durations: dict[str, float],
        course_difficulties: dict[str, int],
    ) -> Optional[list[str]]:
        shortest = graph.shortest_path(start, target)
        if not shortest:
            return None

        reachable: set[str] = set()
        for node in shortest:
            reachable.update(graph.get_transitive_prerequisites(node))
        reachable.update(shortest)

        topo = graph.topological_sort()
        if not topo:
            return shortest

        filtered = [c for c in topo if c in reachable and c in course_difficulties]
        filtered.sort(key=lambda c: course_difficulties.get(c, 0))

        if start.strip().upper() not in filtered:
            filtered.insert(0, start.strip().upper())
        if target.strip().upper() not in filtered:
            filtered.append(target.strip().upper())

        seen: set[str] = set()
        result: list[str] = []
        for code in filtered:
            if code not in seen:
                seen.add(code)
                result.append(code)
        return result if target.strip().upper() in result else shortest


class MinimumDurationStrategy(PathFindingStrategy):
    """Find path minimizing total duration using modified BFS."""

    def find_path(
        self,
        graph: PrerequisiteGraph,
        start: str,
        target: str,
        course_durations: dict[str, float],
        course_difficulties: dict[str, int],
    ) -> Optional[list[str]]:
        all_paths = graph.all_paths(start, target, max_paths=20)
        if not all_paths:
            return graph.shortest_path(start, target)
        return min(
            all_paths,
            key=lambda p: sum(course_durations.get(c, 0) for c in p),
        )


class PathFinder:
    """Context class for Strategy Pattern path finding."""

    def __init__(self, strategy: PathFindingStrategy | None = None) -> None:
        self._strategy = strategy or ShortestPathStrategy()

    def set_strategy(self, strategy: PathFindingStrategy) -> None:
        self._strategy = strategy

    def find_path(
        self,
        graph: PrerequisiteGraph,
        start: str,
        target: str,
        course_durations: dict[str, float],
        course_difficulties: dict[str, int],
    ) -> Optional[list[str]]:
        return self._strategy.find_path(
            graph, start, target, course_durations, course_difficulties
        )

    def find_path_with_stats(
        self,
        graph: PrerequisiteGraph,
        start: str,
        target: str,
        course_durations: dict[str, float],
        course_difficulties: dict[str, int],
    ) -> tuple[Optional[list[str]], Optional[PathStatistics]]:
        path = self.find_path(
            graph, start, target, course_durations, course_difficulties
        )
        if not path:
            return None, None
        stats = compute_path_statistics(path, course_durations, course_difficulties)
        return path, stats


class ProgressObserver(ABC):
    """Observer interface for enrollment events (Observer Pattern)."""

    @abstractmethod
    def on_enrollment_created(self, learner_id: str, course_code: str) -> None:
        """Called when a learner enrolls in a course."""

    @abstractmethod
    def on_enrollment_completed(
        self, learner_id: str, course_code: str, score: Optional[float]
    ) -> None:
        """Called when a learner completes a course."""

    @abstractmethod
    def on_course_updated(self, course_code: str) -> None:
        """Called when course metadata changes."""


class Observable:
    """Mixin providing observer registration and notification."""

    def __init__(self) -> None:
        self._observers: List[ProgressObserver] = []

    def register_observer(self, observer: ProgressObserver) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: ProgressObserver) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def notify_enrollment_created(self, learner_id: str, course_code: str) -> None:
        for observer in self._observers:
            observer.on_enrollment_created(learner_id, course_code)

    def notify_enrollment_completed(
        self, learner_id: str, course_code: str, score: Optional[float]
    ) -> None:
        for observer in self._observers:
            observer.on_enrollment_completed(learner_id, course_code, score)

    def notify_course_updated(self, course_code: str) -> None:
        for observer in self._observers:
            observer.on_course_updated(course_code)


class LoggingObserver(ProgressObserver):
    """Observer that logs events (useful for debugging and audit)."""

    def __init__(self, logger: Callable[[str], None]) -> None:
        self._logger = logger

    def on_enrollment_created(self, learner_id: str, course_code: str) -> None:
        self._logger(f"Enrollment created: {learner_id} -> {course_code}")

    def on_enrollment_completed(
        self, learner_id: str, course_code: str, score: Optional[float]
    ) -> None:
        self._logger(
            f"Enrollment completed: {learner_id} -> {course_code} (score={score})"
        )

    def on_course_updated(self, course_code: str) -> None:
        self._logger(f"Course updated: {course_code}")


class GUIRefreshObserver(ProgressObserver):
    """Observer that triggers GUI refresh callbacks."""

    def __init__(
        self,
        on_refresh: Callable[[], None],
    ) -> None:
        self._on_refresh = on_refresh

    def on_enrollment_created(self, learner_id: str, course_code: str) -> None:
        self._on_refresh()

    def on_enrollment_completed(
        self, learner_id: str, course_code: str, score: Optional[float]
    ) -> None:
        self._on_refresh()

    def on_course_updated(self, course_code: str) -> None:
        self._on_refresh()
