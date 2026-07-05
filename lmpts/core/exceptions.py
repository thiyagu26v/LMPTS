"""Domain-specific exception hierarchy for LMPTS."""


class LMPTSError(Exception):
    """Base exception for all LMPTS domain errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class ValidationError(LMPTSError):
    """Raised when domain validation fails."""


class CourseNotFoundError(LMPTSError):
    """Raised when a requested course does not exist."""


class LearnerNotFoundError(LMPTSError):
    """Raised when a requested learner does not exist."""


class CircularDependencyError(LMPTSError):
    """Raised when a prerequisite would create a cycle."""


class EnrollmentError(LMPTSError):
    """Raised when enrollment business rules are violated."""


class PrerequisiteNotMetError(EnrollmentError):
    """Raised when learner lacks required prerequisites."""


class RepositoryError(LMPTSError):
    """Raised when data access operations fail."""


class DatabaseError(RepositoryError):
    """Raised when database operations fail."""


class ServiceError(LMPTSError):
    """Raised when service-layer orchestration fails."""


class EntityValidationError(ValidationError):
    """Raised when entity creation or update validation fails."""
