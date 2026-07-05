"""Tests for database layer."""

import pytest

from lmpts.core.exceptions import DatabaseError
from lmpts.data.database import DatabaseManager


class TestDatabaseManager:
    def test_singleton(self, temp_db_path):
        DatabaseManager.reset_instance()
        db1 = DatabaseManager(temp_db_path)
        db2 = DatabaseManager(temp_db_path)
        assert db1 is db2
        DatabaseManager.reset_instance()

    def test_initialize_creates_tables(self, db_manager):
        row = db_manager.fetchone(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='courses'"
        )
        assert row is not None

    def test_seed_data_loaded(self, db_manager):
        row = db_manager.fetchone("SELECT COUNT(*) as cnt FROM courses")
        assert row["cnt"] > 0

    def test_foreign_keys_enabled(self, db_manager):
        row = db_manager.fetchone("PRAGMA foreign_keys")
        assert row[0] == 1

    def test_transaction_rollback(self, db_manager):
        initial = db_manager.fetchone("SELECT COUNT(*) as cnt FROM courses")["cnt"]
        try:
            with db_manager.transaction() as conn:
                conn.execute(
                    "INSERT INTO courses (code, name, description, difficulty, duration_hours) "
                    "VALUES ('ROLLBACK1', 'Test', '', 'beginner', 10)"
                )
                raise ValueError("Force rollback")
        except (DatabaseError, ValueError):
            pass
        after = db_manager.fetchone("SELECT COUNT(*) as cnt FROM courses")["cnt"]
        assert after == initial

    def test_reset_instance(self, temp_db_path):
        DatabaseManager.reset_instance()
        db = DatabaseManager(temp_db_path)
        db.initialize()
        DatabaseManager.reset_instance()
        assert DatabaseManager._instance is None
