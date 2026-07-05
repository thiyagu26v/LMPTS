"""Enumerations for categorical domain values."""

from enum import Enum


class DifficultyLevel(str, Enum):
    """Course difficulty levels ordered by complexity."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

    @classmethod
    def from_string(cls, value: str) -> "DifficultyLevel":
        """Parse difficulty from string with validation."""
        normalized = value.strip().lower()
        try:
            return cls(normalized)
        except ValueError as exc:
            valid = ", ".join(m.value for m in cls)
            raise ValueError(
                f"Invalid difficulty '{value}'. Valid values: {valid}"
            ) from exc

    @property
    def numeric_rank(self) -> int:
        """Return numeric rank for difficulty progression analysis."""
        return {
            DifficultyLevel.BEGINNER: 1,
            DifficultyLevel.INTERMEDIATE: 2,
            DifficultyLevel.ADVANCED: 3,
            DifficultyLevel.EXPERT: 4,
        }[self]


class CourseStatus(str, Enum):
    """Lifecycle status of a course."""

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

    @classmethod
    def from_string(cls, value: str) -> "CourseStatus":
        """Parse status from string with validation."""
        normalized = value.strip().lower()
        try:
            return cls(normalized)
        except ValueError as exc:
            valid = ", ".join(m.value for m in cls)
            raise ValueError(
                f"Invalid status '{value}'. Valid values: {valid}"
            ) from exc


class EnrollmentStatus(str, Enum):
    """Status of a learner enrollment in a course."""

    ENROLLED = "enrolled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DROPPED = "dropped"

    @classmethod
    def from_string(cls, value: str) -> "EnrollmentStatus":
        """Parse enrollment status from string."""
        normalized = value.strip().lower()
        try:
            return cls(normalized)
        except ValueError as exc:
            valid = ", ".join(m.value for m in cls)
            raise ValueError(
                f"Invalid enrollment status '{value}'. Valid values: {valid}"
            ) from exc
