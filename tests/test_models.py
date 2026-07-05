"""Unit tests for domain models."""

import pytest

from lmpts.core.enums import CourseStatus, DifficultyLevel, EnrollmentStatus
from lmpts.core.exceptions import EntityValidationError
from lmpts.core.models import Course, Enrollment, Learner, PrerequisiteRelation


class TestCourse:
    def test_create_valid_course(self):
        course = Course(
            code="CS101",
            name="Intro",
            description="Intro course",
            difficulty=DifficultyLevel.BEGINNER,
            duration_hours=40.0,
        )
        assert course.code == "CS101"
        is_valid, _ = course.validate()
        assert is_valid

    def test_empty_code_raises_on_validate(self):
        course = Course(
            code="",
            name="Test",
            description="",
            difficulty=DifficultyLevel.BEGINNER,
            duration_hours=10.0,
        )
        is_valid, msg = course.validate()
        assert not is_valid
        assert "empty" in msg.lower()

    def test_negative_duration_invalid(self):
        course = Course(
            code="X1",
            name="Test",
            description="",
            difficulty=DifficultyLevel.BEGINNER,
            duration_hours=-5.0,
        )
        is_valid, msg = course.validate()
        assert not is_valid

    def test_self_prerequisite_raises(self):
        course = Course(
            code="CS101",
            name="Intro",
            description="",
            difficulty=DifficultyLevel.BEGINNER,
            duration_hours=40.0,
        )
        with pytest.raises(EntityValidationError):
            course.add_prerequisite("CS101")

    def test_prerequisites_encapsulation(self):
        course = Course(
            code="CS101",
            name="Intro",
            description="",
            difficulty=DifficultyLevel.BEGINNER,
            duration_hours=40.0,
        )
        course.add_prerequisite("MATH101")
        prereqs = course.prerequisites
        prereqs.add("HACK")
        assert "HACK" not in course.prerequisites

    def test_has_prerequisite_o1(self):
        course = Course(
            code="CS101",
            name="Intro",
            description="",
            difficulty=DifficultyLevel.BEGINNER,
            duration_hours=40.0,
        )
        course.add_prerequisite("MATH101")
        assert course.has_prerequisite("MATH101")
        assert not course.has_prerequisite("PHYS101")

    def test_published_available_for_enrollment(self):
        course = Course(
            code="CS101",
            name="Intro",
            description="",
            difficulty=DifficultyLevel.BEGINNER,
            duration_hours=40.0,
            status=CourseStatus.PUBLISHED,
        )
        assert course.is_available_for_enrollment()

    def test_archived_not_available(self):
        course = Course(
            code="CS101",
            name="Intro",
            description="",
            difficulty=DifficultyLevel.BEGINNER,
            duration_hours=40.0,
            status=CourseStatus.ARCHIVED,
        )
        assert not course.is_available_for_enrollment()


class TestLearner:
    def test_valid_learner(self):
        learner = Learner(learner_id="L001", name="Alice", email="alice@test.com")
        is_valid, _ = learner.validate()
        assert is_valid

    def test_invalid_email(self):
        learner = Learner(learner_id="L001", name="Alice", email="invalid")
        is_valid, msg = learner.validate()
        assert not is_valid

    def test_empty_id(self):
        learner = Learner(learner_id="", name="Alice", email="a@b.com")
        is_valid, _ = learner.validate()
        assert not is_valid


class TestEnrollment:
    def test_valid_enrollment(self):
        e = Enrollment(enrollment_id=1, learner_id="L001", course_code="CS101")
        is_valid, _ = e.validate()
        assert is_valid

    def test_invalid_score(self):
        e = Enrollment(enrollment_id=1, learner_id="L001", course_code="CS101")
        with pytest.raises(EntityValidationError):
            e.mark_completed(150.0)

    def test_mark_completed(self):
        e = Enrollment(enrollment_id=1, learner_id="L001", course_code="CS101")
        e.mark_completed(85.0)
        assert e.status == EnrollmentStatus.COMPLETED
        assert e.score == 85.0
        assert e.is_completed


class TestPrerequisiteRelation:
    def test_valid_relation(self):
        rel = PrerequisiteRelation("CS101", "CS102")
        assert rel.prerequisite_code == "CS101"
        assert rel.dependent_code == "CS102"

    def test_self_prerequisite_raises(self):
        with pytest.raises(EntityValidationError):
            PrerequisiteRelation("CS101", "CS101")
