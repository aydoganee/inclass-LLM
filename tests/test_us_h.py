"""
Tests for US-H: Start/End Activity
Assignee: Oguzhan Elmas
ClickUp: https://app.clickup.com/t/86ex92f2y

Acceptance Criteria:
- Start sets state to ACTIVE
- End sets state to ENDED
- ENDED activity cannot accept new score logs
"""

import hashlib
import pytest
from unittest.mock import patch, MagicMock

INSTRUCTOR_EMAIL = "instructor@test.com"
INSTRUCTOR_PASS = "testpass"
STUDENT_EMAIL = "student@test.com"
STUDENT_PASS = "studentpass"
COURSE_ID = "COURSE-101"
ACTIVITY_NO = 1


def _make_instructor():
    return {
        "id": "inst-1",
        "email": INSTRUCTOR_EMAIL,
        "password_hash": hashlib.sha256(INSTRUCTOR_PASS.encode()).hexdigest(),
    }


def _make_student():
    return {
        "id": "stu-1",
        "email": STUDENT_EMAIL,
        "password_hash": hashlib.sha256(STUDENT_PASS.encode()).hexdigest(),
    }


def _make_activity(status="NOT_STARTED"):
    return {
        "id": "act-1",
        "course_id": COURSE_ID,
        "activity_no": ACTIVITY_NO,
        "activity_text": "Explain the OSI model.",
        "learning_objectives": ["Describe each OSI layer", "Explain encapsulation"],
        "status": status,
    }


def _make_course():
    return {"id": COURSE_ID, "instructor_id": "inst-1"}


def _make_enrollment():
    return {"id": "enr-1", "course_id": COURSE_ID, "student_id": "stu-1"}


# ---------------------------------------------------------------------------
# US-H: startActivity — sets status to ACTIVE
# ---------------------------------------------------------------------------

def test_start_activity_success():
    """Start sets state to ACTIVE."""
    from app.services import startActivity

    instructor = _make_instructor()
    activity = _make_activity("NOT_STARTED")
    course = _make_course()

    with patch("app.services.supabase_client") as mock_sb:
        def table_side_effect(name):
            m = MagicMock()
            if name == "instructors":
                m.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(data=instructor)
            elif name == "courses":
                m.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(data=course)
            elif name == "activities":
                m.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(data=activity)
                m.update.return_value.eq.return_value.execute.return_value = MagicMock(data=activity)
            return m
        mock_sb.table.side_effect = table_side_effect

        result = startActivity(INSTRUCTOR_EMAIL, INSTRUCTOR_PASS, COURSE_ID, ACTIVITY_NO)

    assert result["ok"] is True


def test_start_activity_wrong_password():
    """Invalid credentials must be rejected."""
    from app.services import startActivity

    instructor = {**_make_instructor(), "password_hash": hashlib.sha256(b"other").hexdigest()}

    with patch("app.services.supabase_client") as mock_sb:
        def table_side_effect(name):
            m = MagicMock()
            if name == "instructors":
                m.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(data=instructor)
            return m
        mock_sb.table.side_effect = table_side_effect

        result = startActivity(INSTRUCTOR_EMAIL, "wrongpass", COURSE_ID, ACTIVITY_NO)

    assert result["ok"] is False


def test_start_activity_not_owner():
    """Instructor who does not own the course must be rejected."""
    from app.services import startActivity

    instructor = _make_instructor()

    with patch("app.services.supabase_client") as mock_sb:
        def table_side_effect(name):
            m = MagicMock()
            if name == "instructors":
                m.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(data=instructor)
            elif name == "courses":
                m.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.side_effect = Exception("not found")
            return m
        mock_sb.table.side_effect = table_side_effect

        result = startActivity(INSTRUCTOR_EMAIL, INSTRUCTOR_PASS, "OTHER-COURSE", ACTIVITY_NO)

    assert result["ok"] is False


def test_start_activity_not_found():
    """Non-existent activity must return an error."""
    from app.services import startActivity

    instructor = _make_instructor()
    course = _make_course()

    with patch("app.services.supabase_client") as mock_sb:
        def table_side_effect(name):
            m = MagicMock()
            if name == "instructors":
                m.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(data=instructor)
            elif name == "courses":
                m.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(data=course)
            elif name == "activities":
                m.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.side_effect = Exception("not found")
            return m
        mock_sb.table.side_effect = table_side_effect

        result = startActivity(INSTRUCTOR_EMAIL, INSTRUCTOR_PASS, COURSE_ID, 999)

    assert result["ok"] is False


# ---------------------------------------------------------------------------
# US-H: endActivity — sets status to ENDED
# ---------------------------------------------------------------------------

def test_end_activity_success():
    """End sets state to ENDED."""
    from app.services import endActivity

    instructor = _make_instructor()
    activity = _make_activity("ACTIVE")
    course = _make_course()

    with patch("app.services.supabase_client") as mock_sb:
        def table_side_effect(name):
            m = MagicMock()
            if name == "instructors":
                m.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(data=instructor)
            elif name == "courses":
                m.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(data=course)
            elif name == "activities":
                m.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(data=activity)
                m.update.return_value.eq.return_value.execute.return_value = MagicMock(data=activity)
            return m
        mock_sb.table.side_effect = table_side_effect

        result = endActivity(INSTRUCTOR_EMAIL, INSTRUCTOR_PASS, COURSE_ID, ACTIVITY_NO)

    assert result["ok"] is True


def test_ended_activity_rejects_score_log():
    """ENDED activity cannot accept new score logs."""
    from app.services import logScore

    student = _make_student()
    activity = _make_activity("ENDED")
    enrollment = _make_enrollment()

    with patch("app.services.supabase_client") as mock_sb:
        def table_side_effect(name):
            m = MagicMock()
            if name == "students":
                m.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(data=student)
            elif name == "enrollments":
                m.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(data=enrollment)
            elif name == "activities":
                m.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(data=activity)
            return m
        mock_sb.table.side_effect = table_side_effect

        result = logScore(STUDENT_EMAIL, STUDENT_PASS, COURSE_ID, ACTIVITY_NO, score=1.0)

    assert result["ok"] is False


def test_end_activity_wrong_instructor():
    """Non-existent instructor must be rejected."""
    from app.services import endActivity

    with patch("app.services.supabase_client") as mock_sb:
        def table_side_effect(name):
            m = MagicMock()
            if name == "instructors":
                m.select.return_value.eq.return_value.single.return_value.execute.side_effect = Exception("not found")
            return m
        mock_sb.table.side_effect = table_side_effect

        result = endActivity("nobody@test.com", "wrong", COURSE_ID, ACTIVITY_NO)

    assert result["ok"] is False
