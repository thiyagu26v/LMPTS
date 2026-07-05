"""Pytest fixtures for LMPTS tests."""

import pytest
from pathlib import Path

from lmpts.data.database import DatabaseManager
from lmpts.services.container import ServiceContainer


@pytest.fixture
def temp_db_path(tmp_path: Path) -> Path:
    return tmp_path / "test_lmpts.db"


@pytest.fixture
def db_manager(temp_db_path: Path) -> DatabaseManager:
    DatabaseManager.reset_instance()
    manager = DatabaseManager(temp_db_path)
    manager.initialize()
    yield manager
    manager.close()
    DatabaseManager.reset_instance()


@pytest.fixture
def container(temp_db_path: Path) -> ServiceContainer:
    DatabaseManager.reset_instance()
    svc = ServiceContainer(temp_db_path)
    yield svc
    svc.db.close()
    DatabaseManager.reset_instance()


@pytest.fixture
def sample_course_data() -> dict:
    return {
        "code": "TEST101",
        "name": "Test Course",
        "description": "A test course",
        "difficulty": "beginner",
        "duration_hours": 30.0,
        "instructor": "Test Instructor",
    }
