"""Tests for repository layer."""

import pytest

from lmpts.core.enums import CourseStatus, DifficultyLevel, EnrollmentStatus
from lmpts.core.exceptions import RepositoryError
from lmpts.core.models import Course, Enrollment, Learner, PrerequisiteRelation
from lmpts.core.patterns import CourseFactory, LearnerFactory
from lmpts.data.repository import (
    CourseRepository,
    EnrollmentRepository,
    LearnerRepository,
    PrerequisiteRepository,
)


class TestCourseRepository:
    def test_crud(self, db_manager):
        repo = CourseRepository(db_manager)
        course = CourseFactory.create(
            code="REPO101",
            name="Repo Test",
            description="Test",
            difficulty="beginner",
            duration_hours=20.0,
        )
        repo.create(course)
        fetched = repo.read("REPO101")
        assert fetched is not None
        assert fetched.name == "Repo Test"

        fetched.name = "Updated"
        repo.update(fetched)
        updated = repo.read("REPO101")
        assert updated.name == "Updated"

        assert repo.delete("REPO101")
        assert repo.read("REPO101") is None

    def test_search(self, db_manager):
        repo = CourseRepository(db_manager)
        results = repo.search("CS101")
        assert len(results) >= 1

    def test_list_by_status(self, db_manager):
        repo = CourseRepository(db_manager)
        published = repo.list_by_status(CourseStatus.PUBLISHED)
        assert all(c.status == CourseStatus.PUBLISHED for c in published)


class TestLearnerRepository:
    def test_crud(self, db_manager):
        repo = LearnerRepository(db_manager)
        learner = LearnerFactory.create("LR001", "Test User", "test@test.com")
        repo.create(learner)
        assert repo.exists("LR001")
        fetched = repo.read("LR001")
        assert fetched.name == "Test User"
        repo.delete("LR001")
        assert not repo.exists("LR001")


class TestEnrollmentRepository:
    def test_create_and_find(self, db_manager):
        course_repo = CourseRepository(db_manager)
        learner_repo = LearnerRepository(db_manager)
        enroll_repo = EnrollmentRepository(db_manager)

        course_repo.create(
            CourseFactory.create(
                code="ENR101", name="E", description="", difficulty="beginner", duration_hours=10
            )
        )
        learner_repo.create(LearnerFactory.create("EL001", "E Learner", "e@test.com"))

        enrollment = Enrollment(
            enrollment_id=None, learner_id="EL001", course_code="ENR101"
        )
        saved = enroll_repo.create(enrollment)
        assert saved.enrollment_id is not None

        found = enroll_repo.find_by_learner_and_course("EL001", "ENR101")
        assert found is not None


class TestPrerequisiteRepository:
    def test_add_and_list(self, db_manager):
        course_repo = CourseRepository(db_manager)
        prereq_repo = PrerequisiteRepository(db_manager)

        for code in ["PRA", "PRB"]:
            course_repo.create(
                CourseFactory.create(
                    code=code, name=code, description="", difficulty="beginner", duration_hours=10
                )
            )

        rel = PrerequisiteRelation("PRA", "PRB")
        prereq_repo.add(rel)
        assert prereq_repo.exists("PRA", "PRB")
        edges = prereq_repo.get_all_edges()
        assert ("PRA", "PRB") in edges

        assert prereq_repo.remove("PRA", "PRB")
        assert not prereq_repo.exists("PRA", "PRB")
