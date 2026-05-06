"""
Tests for US-I: Student Access Control
Assignee: Oguzhan Elmas
ClickUp: https://app.clickup.com/t/[US-I-ID]

Acceptance Criteria:
- NOT_STARTED activity is not accessible
- ACTIVE activity returns activity text without exposing learning objectives
- ENDED activity is not accessible
- Non-enrolled or unauthorized student access is rejected
"""

import hashlib
import pytest
from unittest.mock import patch, MagicMock

STUDENT_EMAIL = "student@test.com"
STUDENT_PASS = "studentpass"
COURSE_ID = "COURSE-101"
ACTIVITY_NO = 1


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


def _make_enrollment():
    return {"id": "enr-1", "course_id": COURSE_ID, "student_id": "stu-1"}


# ---------------------------------------------------------------------------
# US-I: getActivity — student access control
# ---------------------------------------------------------------------------

def test_not_started_activity_is_blocked():
    """NOT_STARTED activity must not be accessible."""
    from app.services import getActivity

    student = _make_student()
    activity = _make_activity("NOT_STARTED")
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

        result = getActivity(STUDENT_EMAIL, STUDENT_PASS, COURSE_ID, ACTIVITY_NO)

    assert result["ok"] is False


def test_active_activity_returns_text_without_objectives():
    """ACTIVE activity returns activity_text; learning_objectives must NOT be exposed."""
    from app.services import getActivity

    student = _make_student()
    activity = _make_activity("ACTIVE")
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

        result = getActivity(STUDENT_EMAIL, STUDENT_PASS, COURSE_ID, ACTIVITY_NO)

    assert result["ok"] is True
    assert "activity" in result
    assert "activity_text" in result["activity"]
    assert "learning_objectives" not in result["activity"]


def test_ended_activity_is_blocked():
    """ENDED activity must not be accessible."""
    from app.services import getActivity

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

        result = getActivity(STUDENT_EMAIL, STUDENT_PASS, COURSE_ID, ACTIVITY_NO)

    assert result["ok"] is False


def test_unenrolled_student_is_rejected():
    """Student not enrolled in the course must be rejected."""
    from app.services import getActivity

    student = _make_student()

    with patch("app.services.supabase_client") as mock_sb:
        def table_side_effect(name):
            m = MagicMock()
            if name == "students":
                m.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(data=student)
            elif name == "enrollments":
                m.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.side_effect = Exception("not found")
            return m
        mock_sb.table.side_effect = table_side_effect

        result = getActivity(STUDENT_EMAIL, STUDENT_PASS, COURSE_ID, ACTIVITY_NO)

    assert result["ok"] is False


def test_invalid_student_credentials():
    """Student with wrong credentials must be rejected."""
    from app.services import getActivity

    with patch("app.services.supabase_client") as mock_sb:
        def table_side_effect(name):
            m = MagicMock()
            if name == "students":
                m.select.return_value.eq.return_value.single.return_value.execute.side_effect = Exception("not found")
            return m
        mock_sb.table.side_effect = table_side_effect

        result = getActivity("nobody@test.com", "badpass", COURSE_ID, ACTIVITY_NO)

    assert result["ok"] is False
