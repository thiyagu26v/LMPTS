"""Repository implementations for data access abstraction."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import List, Optional, Set, Tuple

from lmpts.core.enums import CourseStatus, DifficultyLevel, EnrollmentStatus
from lmpts.core.exceptions import DatabaseError, RepositoryError
from lmpts.core.models import Course, Enrollment, Learner, PrerequisiteRelation
from lmpts.core.patterns import Repository
from lmpts.data.database import DatabaseManager

logger = logging.getLogger(__name__)


def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")


class CourseRepository(Repository[Course]):
    """SQLite-backed course repository."""

    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def create(self, entity: Course) -> Course:
        try:
            with self._db.transaction() as conn:
                conn.execute(
                    """INSERT INTO courses (code, name, description, difficulty,
                       duration_hours, instructor, status)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        entity.code,
                        entity.name,
                        entity.description,
                        entity.difficulty.value,
                        entity.duration_hours,
                        entity.instructor,
                        entity.status.value,
                    ),
                )
            return entity
        except Exception as exc:
            raise RepositoryError(f"Failed to create course {entity.code}: {exc}") from exc

    def read(self, entity_id: str) -> Optional[Course]:
        row = self._db.fetchone(
            "SELECT * FROM courses WHERE code = ?", (entity_id.strip().upper(),)
        )
        return self._row_to_course(row) if row else None

    def update(self, entity: Course) -> Course:
        try:
            with self._db.transaction() as conn:
                conn.execute(
                    """UPDATE courses SET name=?, description=?, difficulty=?,
                       duration_hours=?, instructor=?, status=?,
                       updated_at=datetime('now')
                       WHERE code=?""",
                    (
                        entity.name,
                        entity.description,
                        entity.difficulty.value,
                        entity.duration_hours,
                        entity.instructor,
                        entity.status.value,
                        entity.code,
                    ),
                )
            entity.touch()
            return entity
        except Exception as exc:
            raise RepositoryError(f"Failed to update course {entity.code}: {exc}") from exc

    def delete(self, entity_id: str) -> bool:
        code = entity_id.strip().upper()
        try:
            with self._db.transaction() as conn:
                cursor = conn.execute("DELETE FROM courses WHERE code = ?", (code,))
                return cursor.rowcount > 0
        except Exception as exc:
            raise RepositoryError(f"Failed to delete course {code}: {exc}") from exc

    def list_all(self) -> List[Course]:
        rows = self._db.fetchall("SELECT * FROM courses ORDER BY code")
        return [self._row_to_course(row) for row in rows]

    def list_by_status(self, status: CourseStatus) -> List[Course]:
        rows = self._db.fetchall(
            "SELECT * FROM courses WHERE status = ? ORDER BY code",
            (status.value,),
        )
        return [self._row_to_course(row) for row in rows]

    def search(self, query: str) -> List[Course]:
        pattern = f"%{query.strip()}%"
        rows = self._db.fetchall(
            """SELECT * FROM courses
               WHERE code LIKE ? OR name LIKE ? OR instructor LIKE ?
               ORDER BY code""",
            (pattern, pattern, pattern),
        )
        return [self._row_to_course(row) for row in rows]

    def exists(self, code: str) -> bool:
        row = self._db.fetchone(
            "SELECT 1 FROM courses WHERE code = ?", (code.strip().upper(),)
        )
        return row is not None

    def _row_to_course(self, row) -> Course:
        course = Course(
            code=row["code"],
            name=row["name"],
            description=row["description"],
            difficulty=DifficultyLevel.from_string(row["difficulty"]),
            duration_hours=row["duration_hours"],
            instructor=row["instructor"],
            status=CourseStatus.from_string(row["status"]),
        )
        return course


class LearnerRepository(Repository[Learner]):
    """SQLite-backed learner repository."""

    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def create(self, entity: Learner) -> Learner:
        try:
            with self._db.transaction() as conn:
                conn.execute(
                    "INSERT INTO learners (learner_id, name, email) VALUES (?, ?, ?)",
                    (entity.learner_id, entity.name, entity.email),
                )
            return entity
        except Exception as exc:
            raise RepositoryError(
                f"Failed to create learner {entity.learner_id}: {exc}"
            ) from exc

    def read(self, entity_id: str) -> Optional[Learner]:
        row = self._db.fetchone(
            "SELECT * FROM learners WHERE learner_id = ?", (entity_id.strip(),)
        )
        return self._row_to_learner(row) if row else None

    def update(self, entity: Learner) -> Learner:
        try:
            with self._db.transaction() as conn:
                conn.execute(
                    """UPDATE learners SET name=?, email=?,
                       updated_at=datetime('now') WHERE learner_id=?""",
                    (entity.name, entity.email, entity.learner_id),
                )
            entity.touch()
            return entity
        except Exception as exc:
            raise RepositoryError(
                f"Failed to update learner {entity.learner_id}: {exc}"
            ) from exc

    def delete(self, entity_id: str) -> bool:
        try:
            with self._db.transaction() as conn:
                cursor = conn.execute(
                    "DELETE FROM learners WHERE learner_id = ?", (entity_id.strip(),)
                )
                return cursor.rowcount > 0
        except Exception as exc:
            raise RepositoryError(
                f"Failed to delete learner {entity_id}: {exc}"
            ) from exc

    def list_all(self) -> List[Learner]:
        rows = self._db.fetchall("SELECT * FROM learners ORDER BY learner_id")
        return [self._row_to_learner(row) for row in rows]

    def exists(self, learner_id: str) -> bool:
        row = self._db.fetchone(
            "SELECT 1 FROM learners WHERE learner_id = ?", (learner_id.strip(),)
        )
        return row is not None

    def _row_to_learner(self, row) -> Learner:
        return Learner(
            learner_id=row["learner_id"],
            name=row["name"],
            email=row["email"],
        )


class EnrollmentRepository(Repository[Enrollment]):
    """SQLite-backed enrollment repository."""

    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def create(self, entity: Enrollment) -> Enrollment:
        try:
            with self._db.transaction() as conn:
                cursor = conn.execute(
                    """INSERT INTO enrollments (learner_id, course_code, status, score)
                       VALUES (?, ?, ?, ?)""",
                    (
                        entity.learner_id,
                        entity.course_code,
                        entity.status.value,
                        entity.score,
                    ),
                )
                entity.enrollment_id = cursor.lastrowid
            return entity
        except Exception as exc:
            raise RepositoryError(
                f"Failed to create enrollment: {exc}"
            ) from exc

    def read(self, entity_id: str) -> Optional[Enrollment]:
        row = self._db.fetchone(
            "SELECT * FROM enrollments WHERE id = ?", (int(entity_id),)
        )
        return self._row_to_enrollment(row) if row else None

    def update(self, entity: Enrollment) -> Enrollment:
        try:
            with self._db.transaction() as conn:
                conn.execute(
                    """UPDATE enrollments SET status=?, score=?,
                       completed_at=?, updated_at=datetime('now')
                       WHERE id=?""",
                    (
                        entity.status.value,
                        entity.score,
                        entity.completed_at.isoformat() if entity.completed_at else None,
                        entity.enrollment_id,
                    ),
                )
            entity.touch()
            return entity
        except Exception as exc:
            raise RepositoryError(f"Failed to update enrollment: {exc}") from exc

    def delete(self, entity_id: str) -> bool:
        try:
            with self._db.transaction() as conn:
                cursor = conn.execute(
                    "DELETE FROM enrollments WHERE id = ?", (int(entity_id),)
                )
                return cursor.rowcount > 0
        except Exception as exc:
            raise RepositoryError(f"Failed to delete enrollment: {exc}") from exc

    def list_all(self) -> List[Enrollment]:
        rows = self._db.fetchall("SELECT * FROM enrollments ORDER BY id")
        return [self._row_to_enrollment(row) for row in rows]

    def find_by_learner_and_course(
        self, learner_id: str, course_code: str
    ) -> Optional[Enrollment]:
        row = self._db.fetchone(
            """SELECT * FROM enrollments
               WHERE learner_id = ? AND course_code = ?""",
            (learner_id.strip(), course_code.strip().upper()),
        )
        return self._row_to_enrollment(row) if row else None

    def list_by_learner(self, learner_id: str) -> List[Enrollment]:
        rows = self._db.fetchall(
            "SELECT * FROM enrollments WHERE learner_id = ? ORDER BY enrolled_at",
            (learner_id.strip(),),
        )
        return [self._row_to_enrollment(row) for row in rows]

    def list_by_course(self, course_code: str) -> List[Enrollment]:
        rows = self._db.fetchall(
            "SELECT * FROM enrollments WHERE course_code = ? ORDER BY enrolled_at",
            (course_code.strip().upper(),),
        )
        return [self._row_to_enrollment(row) for row in rows]

    def list_completed_by_learner(self, learner_id: str) -> List[Enrollment]:
        rows = self._db.fetchall(
            """SELECT * FROM enrollments
               WHERE learner_id = ? AND status = 'completed'""",
            (learner_id.strip(),),
        )
        return [self._row_to_enrollment(row) for row in rows]

    def count_by_status(self, status: EnrollmentStatus) -> int:
        row = self._db.fetchone(
            "SELECT COUNT(*) as cnt FROM enrollments WHERE status = ?",
            (status.value,),
        )
        return row["cnt"] if row else 0

    def _row_to_enrollment(self, row) -> Enrollment:
        enrollment = Enrollment(
            enrollment_id=row["id"],
            learner_id=row["learner_id"],
            course_code=row["course_code"],
            status=EnrollmentStatus.from_string(row["status"]),
            score=row["score"],
            enrolled_at=_parse_datetime(row["enrolled_at"]),
            completed_at=_parse_datetime(row["completed_at"]),
        )
        return enrollment


class PrerequisiteRepository:
    """Repository for prerequisite relationships."""

    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def add(self, relation: PrerequisiteRelation) -> PrerequisiteRelation:
        try:
            with self._db.transaction() as conn:
                conn.execute(
                    """INSERT INTO prerequisites (prerequisite_code, dependent_code)
                       VALUES (?, ?)""",
                    (relation.prerequisite_code, relation.dependent_code),
                )
            return relation
        except Exception as exc:
            raise RepositoryError(
                f"Failed to add prerequisite {relation.prerequisite_code} -> "
                f"{relation.dependent_code}: {exc}"
            ) from exc

    def remove(self, prerequisite_code: str, dependent_code: str) -> bool:
        try:
            with self._db.transaction() as conn:
                cursor = conn.execute(
                    """DELETE FROM prerequisites
                       WHERE prerequisite_code = ? AND dependent_code = ?""",
                    (
                        prerequisite_code.strip().upper(),
                        dependent_code.strip().upper(),
                    ),
                )
                return cursor.rowcount > 0
        except Exception as exc:
            raise RepositoryError(f"Failed to remove prerequisite: {exc}") from exc

    def list_all(self) -> List[PrerequisiteRelation]:
        rows = self._db.fetchall(
            "SELECT prerequisite_code, dependent_code FROM prerequisites"
        )
        return [
            PrerequisiteRelation(row["prerequisite_code"], row["dependent_code"])
            for row in rows
        ]

    def list_for_course(self, course_code: str) -> List[PrerequisiteRelation]:
        code = course_code.strip().upper()
        rows = self._db.fetchall(
            """SELECT prerequisite_code, dependent_code FROM prerequisites
               WHERE dependent_code = ?""",
            (code,),
        )
        return [
            PrerequisiteRelation(row["prerequisite_code"], row["dependent_code"])
            for row in rows
        ]

    def get_all_edges(self) -> List[Tuple[str, str]]:
        rows = self._db.fetchall(
            "SELECT prerequisite_code, dependent_code FROM prerequisites"
        )
        return [(row["prerequisite_code"], row["dependent_code"]) for row in rows]

    def exists(self, prerequisite_code: str, dependent_code: str) -> bool:
        row = self._db.fetchone(
            """SELECT 1 FROM prerequisites
               WHERE prerequisite_code = ? AND dependent_code = ?""",
            (
                prerequisite_code.strip().upper(),
                dependent_code.strip().upper(),
            ),
        )
        return row is not None
