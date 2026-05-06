"""
Tests for US-G: Update Activity
Assignee: Oguzhan Elmas
ClickUp: https://app.clickup.com/t/[US-G-ID]

Acceptance Criteria:
- Only allowed fields can be updated (activity_text, learning_objectives)
- Empty patch is rejected
- Non-existent activity returns a clear error
"""

import hashlib
import pytest
from unittest.mock import patch, MagicMock

INSTRUCTOR_EMAIL = "instructor@test.com"
INSTRUCTOR_PASS = "testpass"
COURSE_ID = "COURSE-101"
ACTIVITY_NO = 1


def _make_instructor():
    return {
        "id": "inst-1",
        "email": INSTRUCTOR_EMAIL,
        "password_hash": hashlib.sha256(INSTRUCTOR_PASS.encode()).hexdigest(),
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


# ---------------------------------------------------------------------------
# US-G: updateActivity
# ---------------------------------------------------------------------------

def test_update_activity_text_success():
    """activity_text can be updated successfully."""
    from app.services import updateActivity

    instructor = _make_instructor()
    activity = _make_activity()
    course = _make_course()
    updated = {**activity, "activity_text": "New text."}

    with patch("app.services.supabase_client") as mock_sb:
        def table_side_effect(name):
            m = MagicMock()
            if name == "instructors":
                m.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(data=instructor)
            elif name == "courses":
                m.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(data=course)
            elif name == "activities":
                m.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(data=activity)
                m.update.return_value.eq.return_value.execute.return_value = MagicMock(data=[updated])
            return m
        mock_sb.table.side_effect = table_side_effect

        result = updateActivity(
            INSTRUCTOR_EMAIL, INSTRUCTOR_PASS, COURSE_ID, ACTIVITY_NO,
            patch={"activity_text": "New text."}
        )

    assert result["ok"] is True


def test_update_learning_objectives_success():
    """learning_objectives can be updated successfully."""
    from app.services import updateActivity

    instructor = _make_instructor()
    activity = _make_activity()
    course = _make_course()
    new_objectives = ["New objective 1", "New objective 2"]
    updated = {**activity, "learning_objectives": new_objectives}

    with patch("app.services.supabase_client") as mock_sb:
        def table_side_effect(name):
            m = MagicMock()
            if name == "instructors":
                m.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(data=instructor)
            elif name == "courses":
                m.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(data=course)
            elif name == "activities":
                m.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(data=activity)
                m.update.return_value.eq.return_value.execute.return_value = MagicMock(data=[updated])
            return m
        mock_sb.table.side_effect = table_side_effect

        result = updateActivity(
            INSTRUCTOR_EMAIL, INSTRUCTOR_PASS, COURSE_ID, ACTIVITY_NO,
            patch={"learning_objectives": new_objectives}
        )

    assert result["ok"] is True


def test_empty_patch_is_rejected():
    """Empty patch must be rejected."""
    from app.services import updateActivity

    instructor = _make_instructor()
    course = _make_course()

    with patch("app.services.supabase_client") as mock_sb:
        def table_side_effect(name):
            m = MagicMock()
            if name == "instructors":
                m.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(data=instructor)
            elif name == "courses":
                m.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(data=course)
            return m
        mock_sb.table.side_effect = table_side_effect

        result = updateActivity(
            INSTRUCTOR_EMAIL, INSTRUCTOR_PASS, COURSE_ID, ACTIVITY_NO,
            patch={}
        )

    assert result["ok"] is False


def test_disallowed_fields_are_rejected():
    """Fields like 'status' must not be updatable (treated as empty patch)."""
    from app.services import updateActivity

    instructor = _make_instructor()
    course = _make_course()

    with patch("app.services.supabase_client") as mock_sb:
        def table_side_effect(name):
            m = MagicMock()
            if name == "instructors":
                m.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(data=instructor)
            elif name == "courses":
                m.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(data=course)
            return m
        mock_sb.table.side_effect = table_side_effect

        result = updateActivity(
            INSTRUCTOR_EMAIL, INSTRUCTOR_PASS, COURSE_ID, ACTIVITY_NO,
            patch={"status": "ACTIVE"}
        )

    assert result["ok"] is False


def test_nonexistent_activity_returns_error():
    """Non-existent activity must return a clear error."""
    from app.services import updateActivity

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

        result = updateActivity(
            INSTRUCTOR_EMAIL, INSTRUCTOR_PASS, COURSE_ID, 9999,
            patch={"activity_text": "Updated text"}
        )

    assert result["ok"] is False


def test_unauthorized_instructor_is_rejected():
    """Instructor not owning the course must be rejected."""
    from app.services import updateActivity

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

        result = updateActivity(
            INSTRUCTOR_EMAIL, INSTRUCTOR_PASS, "OTHER-COURSE", ACTIVITY_NO,
            patch={"activity_text": "Unauthorized update"}
        )

    assert result["ok"] is False
