"""Domain models with OOP principles: inheritance, encapsulation, abstraction."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Set

from lmpts.core.enums import CourseStatus, DifficultyLevel, EnrollmentStatus
from lmpts.core.exceptions import EntityValidationError


class Identifiable(ABC):
    """Abstract base for entities with unique identifiers."""

    @property
    @abstractmethod
    def id(self) -> str:
        """Return the unique identifier."""

    @abstractmethod
    def validate(self) -> tuple[bool, str]:
        """Validate entity state; return (is_valid, message)."""


class TimestampedEntity(Identifiable, ABC):
    """Base entity with creation and update timestamps."""

    def __init__(self) -> None:
        self._created_at: datetime = datetime.utcnow()
        self._updated_at: datetime = datetime.utcnow()

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    def touch(self) -> None:
        """Update the modification timestamp."""
        self._updated_at = datetime.utcnow()


@dataclass
class Course(TimestampedEntity):
    """Course domain model with encapsulated prerequisite set."""

    code: str
    name: str
    description: str
    difficulty: DifficultyLevel
    duration_hours: float
    instructor: str = ""
    status: CourseStatus = CourseStatus.DRAFT
    _prerequisites: Set[str] = field(default_factory=set, repr=False)

    def __post_init__(self) -> None:
        TimestampedEntity.__init__(self)
        self._code = self.code.strip().upper()
        self.code = self._code

    @property
    def id(self) -> str:
        return self.code

    @property
    def prerequisites(self) -> Set[str]:
        """Return a copy to prevent external mutation."""
        return self._prerequisites.copy()

    def add_prerequisite(self, prereq_code: str) -> None:
        """Add a prerequisite with validation."""
        code = prereq_code.strip().upper()
        if not code:
            raise EntityValidationError("Prerequisite code cannot be empty")
        if code == self._code:
            raise EntityValidationError("Self-prerequisite not allowed")
        self._prerequisites.add(code)
        self.touch()

    def remove_prerequisite(self, prereq_code: str) -> None:
        """Remove a prerequisite relationship."""
        self._prerequisites.discard(prereq_code.strip().upper())
        self.touch()

    def has_prerequisite(self, code: str) -> bool:
        """O(1) membership test for direct prerequisites."""
        return code.strip().upper() in self._prerequisites

    def set_prerequisites(self, codes: Set[str]) -> None:
        """Replace all prerequisites."""
        normalized = {c.strip().upper() for c in codes if c.strip()}
        if self._code in normalized:
            raise EntityValidationError("Self-prerequisite not allowed")
        self._prerequisites = normalized
        self.touch()

    def validate(self) -> tuple[bool, str]:
        """Validate course fields."""
        if not self._code:
            return False, "Course code cannot be empty"
        if not self.name.strip():
            return False, "Course name cannot be empty"
        if self.duration_hours < 0:
            return False, "Duration cannot be negative"
        if self.duration_hours == 0:
            return False, "Duration must be greater than zero"
        return True, ""

    def is_available_for_enrollment(self) -> bool:
        """Only published courses can be enrolled."""
        return self.status == CourseStatus.PUBLISHED


@dataclass
class Learner(TimestampedEntity):
    """Learner profile with enrollment tracking."""

    learner_id: str
    name: str
    email: str

    def __post_init__(self) -> None:
        TimestampedEntity.__init__(self)
        self.learner_id = self.learner_id.strip()

    @property
    def id(self) -> str:
        return self.learner_id

    def validate(self) -> tuple[bool, str]:
        if not self.learner_id:
            return False, "Learner ID cannot be empty"
        if not self.name.strip():
            return False, "Learner name cannot be empty"
        if not self.email.strip() or "@" not in self.email:
            return False, "Valid email is required"
        return True, ""


@dataclass
class Enrollment(TimestampedEntity):
    """Enrollment record linking learner to course."""

    enrollment_id: Optional[int]
    learner_id: str
    course_code: str
    status: EnrollmentStatus = EnrollmentStatus.ENROLLED
    score: Optional[float] = None
    enrolled_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        TimestampedEntity.__init__(self)
        self.learner_id = self.learner_id.strip()
        self.course_code = self.course_code.strip().upper()
        if self.enrolled_at is None:
            self.enrolled_at = datetime.utcnow()

    @property
    def id(self) -> str:
        return str(self.enrollment_id) if self.enrollment_id else ""

    def validate(self) -> tuple[bool, str]:
        if not self.learner_id:
            return False, "Learner ID cannot be empty"
        if not self.course_code:
            return False, "Course code cannot be empty"
        if self.score is not None:
            if self.score < 0 or self.score > 100:
                return False, "Score must be between 0 and 100"
        return True, ""

    def mark_completed(self, score: Optional[float] = None) -> None:
        """Mark enrollment as completed with optional score."""
        if score is not None:
            if score < 0 or score > 100:
                raise EntityValidationError("Score must be between 0 and 100")
            self.score = score
        self.status = EnrollmentStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.touch()

    def mark_in_progress(self) -> None:
        self.status = EnrollmentStatus.IN_PROGRESS
        self.touch()

    @property
    def is_completed(self) -> bool:
        return self.status == EnrollmentStatus.COMPLETED


@dataclass(frozen=True)
class PrerequisiteRelation:
    """Immutable value object representing a prerequisite edge."""

    prerequisite_code: str
    dependent_code: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "prerequisite_code", self.prerequisite_code.strip().upper()
        )
        object.__setattr__(
            self, "dependent_code", self.dependent_code.strip().upper()
        )
        if not self.prerequisite_code or not self.dependent_code:
            raise EntityValidationError("Both course codes are required")
        if self.prerequisite_code == self.dependent_code:
            raise EntityValidationError("Self-prerequisite not allowed")


@dataclass
class PathStatistics:
    """Statistics for a computed learning path."""

    total_hours: float
    course_count: int
    difficulty_progression: list[int]
    average_difficulty: float

    @property
    def is_difficulty_increasing(self) -> bool:
        if len(self.difficulty_progression) < 2:
            return True
        return all(
            self.difficulty_progression[i] <= self.difficulty_progression[i + 1]
            for i in range(len(self.difficulty_progression) - 1)
        )


@dataclass
class LearnerProgress:
    """Aggregated progress metrics for a learner."""

    learner_id: str
    total_enrollments: int
    completed_count: int
    in_progress_count: int
    completion_rate: float
    completed_courses: list[str]
    in_progress_courses: list[str]
