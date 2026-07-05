"""SQLite database management with Singleton pattern."""

from __future__ import annotations

import logging
import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional

from lmpts.core.exceptions import DatabaseError

logger = logging.getLogger(__name__)

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "lmpts.db"
MIGRATIONS_DIR = Path(__file__).resolve().parent / "migrations"


class DatabaseManager:
    """
    Singleton database connection manager.

    Thread-safe SQLite access with transaction support.
    """

    _instance: Optional["DatabaseManager"] = None
    _lock = threading.Lock()

    def __new__(cls, db_path: Optional[Path] = None) -> "DatabaseManager":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    instance = super().__new__(cls)
                    instance._initialized = False
                    cls._instance = instance
        return cls._instance

    def __init__(self, db_path: Optional[Path] = None) -> None:
        if getattr(self, "_initialized", False):
            return
        self._db_path = db_path or DEFAULT_DB_PATH
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._local = threading.local()
        self._initialized = True
        logger.info("DatabaseManager initialized at %s", self._db_path)

    @classmethod
    def reset_instance(cls) -> None:
        """Reset singleton (for testing)."""
        with cls._lock:
            if cls._instance is not None:
                try:
                    cls._instance.close()
                except Exception:
                    pass
            cls._instance = None

    @property
    def db_path(self) -> Path:
        return self._db_path

    def _get_connection(self) -> sqlite3.Connection:
        if not hasattr(self._local, "connection") or self._local.connection is None:
            conn = sqlite3.connect(
                str(self._db_path),
                check_same_thread=False,
                isolation_level=None,
            )
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            self._local.connection = conn
        return self._local.connection

    @contextmanager
    def connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Yield a database connection."""
        try:
            yield self._get_connection()
        except sqlite3.Error as exc:
            raise DatabaseError(f"Database connection error: {exc}") from exc

    @contextmanager
    def transaction(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager for atomic transactions."""
        conn = self._get_connection()
        try:
            conn.execute("BEGIN")
            yield conn
            conn.execute("COMMIT")
        except Exception as exc:
            conn.execute("ROLLBACK")
            raise DatabaseError(f"Transaction failed: {exc}") from exc

    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a single SQL statement."""
        try:
            with self.connection() as conn:
                return conn.execute(sql, params)
        except sqlite3.Error as exc:
            raise DatabaseError(f"SQL execution failed: {exc}") from exc

    def executemany(self, sql: str, params_list: list) -> None:
        """Execute SQL with multiple parameter sets."""
        try:
            with self.connection() as conn:
                conn.executemany(sql, params_list)
        except sqlite3.Error as exc:
            raise DatabaseError(f"Batch SQL execution failed: {exc}") from exc

    def fetchone(self, sql: str, params: tuple = ()) -> Optional[sqlite3.Row]:
        cursor = self.execute(sql, params)
        return cursor.fetchone()

    def fetchall(self, sql: str, params: tuple = ()) -> list:
        cursor = self.execute(sql, params)
        return cursor.fetchall()

    def initialize(self) -> None:
        """Run migrations and seed data."""
        self._run_migrations()
        self._seed_if_empty()

    def _run_migrations(self) -> None:
        migration_file = MIGRATIONS_DIR / "001_initial_schema.sql"
        if not migration_file.exists():
            raise DatabaseError(f"Migration file not found: {migration_file}")
        schema_sql = migration_file.read_text(encoding="utf-8")
        with self.connection() as conn:
            conn.executescript(schema_sql)
        logger.info("Database migrations applied")

    def _seed_if_empty(self) -> None:
        row = self.fetchone("SELECT COUNT(*) as cnt FROM courses")
        if row and row["cnt"] == 0:
            self._seed_data()
            logger.info("Seed data loaded")

    def _seed_data(self) -> None:
        """Load sample courses, learners, and prerequisites."""
        courses = [
            ("CS101", "Intro to Programming", "Fundamentals of programming", "beginner", 40.0, "Dr. Smith", "published"),
            ("CS102", "Data Structures", "Arrays, lists, trees, graphs", "intermediate", 50.0, "Dr. Smith", "published"),
            ("CS201", "Algorithms", "Sorting, searching, complexity", "intermediate", 45.0, "Dr. Jones", "published"),
            ("CS301", "Advanced Algorithms", "Dynamic programming, NP-completeness", "advanced", 55.0, "Dr. Jones", "published"),
            ("MATH101", "Calculus I", "Limits, derivatives, integrals", "beginner", 60.0, "Dr. Lee", "published"),
            ("MATH201", "Linear Algebra", "Vectors, matrices, eigenvalues", "intermediate", 50.0, "Dr. Lee", "published"),
            ("WEB101", "Web Development", "HTML, CSS, JavaScript basics", "beginner", 35.0, "Dr. Chen", "published"),
            ("DB201", "Database Systems", "SQL, normalization, indexing", "intermediate", 45.0, "Dr. Patel", "published"),
        ]
        learners = [
            ("L001", "Alice Johnson", "alice@university.edu"),
            ("L002", "Bob Williams", "bob@university.edu"),
            ("L003", "Carol Davis", "carol@university.edu"),
        ]
        prerequisites = [
            ("CS101", "CS102"),
            ("CS102", "CS201"),
            ("CS201", "CS301"),
            ("MATH101", "MATH201"),
            ("MATH101", "CS201"),
            ("WEB101", "DB201"),
            ("CS101", "WEB101"),
        ]

        with self.transaction() as conn:
            conn.executemany(
                """INSERT INTO courses (code, name, description, difficulty,
                   duration_hours, instructor, status)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                courses,
            )
            conn.executemany(
                "INSERT INTO learners (learner_id, name, email) VALUES (?, ?, ?)",
                learners,
            )
            conn.executemany(
                "INSERT INTO prerequisites (prerequisite_code, dependent_code) VALUES (?, ?)",
                prerequisites,
            )
            conn.execute(
                """INSERT INTO enrollments (learner_id, course_code, status, score)
                   VALUES ('L001', 'CS101', 'completed', 92.5)"""
            )
            conn.execute(
                """INSERT INTO enrollments (learner_id, course_code, status)
                   VALUES ('L001', 'CS102', 'in_progress')"""
            )
            conn.execute(
                """INSERT INTO enrollments (learner_id, course_code, status, score)
                   VALUES ('L002', 'CS101', 'completed', 88.0)"""
            )
            conn.execute(
                """INSERT INTO enrollments (learner_id, course_code, status, score)
                   VALUES ('L002', 'MATH101', 'completed', 95.0)"""
            )

    def close(self) -> None:
        if hasattr(self._local, "connection") and self._local.connection:
            self._local.connection.close()
            self._local.connection = None
