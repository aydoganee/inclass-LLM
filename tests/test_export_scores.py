"""
US-T3: Export Scores — Validate CSV format and content
Owner: Oğuzhan Elmas
"""

import csv
import hashlib
import io
import pytest
from unittest.mock import patch, MagicMock


INSTRUCTOR_EMAIL = "instructor@test.com"
INSTRUCTOR_PASS = "testpass"
COURSE_ID = "COURSE-101"
ACTIVITY_NO = 1

EXPECTED_HEADERS = ["student_email", "score", "meta", "created_at"]


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def _make_instructor():
    return {
        "id": "inst-1",
        "email": INSTRUCTOR_EMAIL,
        "password_hash": _hash(INSTRUCTOR_PASS),
    }


def _make_course():
    return {"id": COURSE_ID, "instructor_id": "inst-1"}


def _make_activity(status="ENDED"):
    return {
        "id": "act-1",
        "course_id": COURSE_ID,
        "activity_no": ACTIVITY_NO,
        "activity_text": "Explain the OSI model.",
        "learning_objectives": ["Describe each OSI layer"],
        "status": status,
    }


def _make_score_row(email: str, score: float, meta: str = "", created_at: str = "2026-05-11T10:00:00"):
    return {
        "id": f"score-{email}",
        "activity_id": "act-1",
        "score": score,
        "meta": meta,
        "created_at": created_at,
        "students": {"email": email},
    }


def _build_mock(scores: list):
    """Build a supabase_client mock that returns the given score rows."""
    instructor = _make_instructor()
    course = _make_course()
    activity = _make_activity()

    def table_side_effect(name):
        m = MagicMock()
        if name == "instructors":
            m.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(data=instructor)
        elif name == "courses":
            m.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(data=course)
        elif name == "activities":
            m.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(data=activity)
        elif name == "scores":
            m.select.return_value.eq.return_value.execute.return_value = MagicMock(data=scores)
        return m

    mock_sb = MagicMock()
    mock_sb.table.side_effect = table_side_effect
    return mock_sb


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestExportScoresCSVFormat:
    """Validate that exportScores returns a well-formed CSV with correct headers."""

    def test_returns_ok_true(self):
        from app.services import exportScores
        with patch("app.services.supabase_client", _build_mock([])):
            result = exportScores(INSTRUCTOR_EMAIL, INSTRUCTOR_PASS, COURSE_ID, ACTIVITY_NO)
        assert result["ok"] is True

    def test_csv_key_present(self):
        from app.services import exportScores
        with patch("app.services.supabase_client", _build_mock([])):
            result = exportScores(INSTRUCTOR_EMAIL, INSTRUCTOR_PASS, COURSE_ID, ACTIVITY_NO)
        assert "csv" in result

    def test_csv_headers_correct(self):
        """First row must be exactly: student_email,score,meta,created_at"""
        from app.services import exportScores
        with patch("app.services.supabase_client", _build_mock([])):
            result = exportScores(INSTRUCTOR_EMAIL, INSTRUCTOR_PASS, COURSE_ID, ACTIVITY_NO)
        reader = csv.reader(io.StringIO(result["csv"]))
        headers = next(reader)
        assert headers == EXPECTED_HEADERS

    def test_csv_header_order(self):
        """Column order must match the spec: student_email first, created_at last."""
        from app.services import exportScores
        with patch("app.services.supabase_client", _build_mock([])):
            result = exportScores(INSTRUCTOR_EMAIL, INSTRUCTOR_PASS, COURSE_ID, ACTIVITY_NO)
        reader = csv.reader(io.StringIO(result["csv"]))
        headers = next(reader)
        assert headers[0] == "student_email"
        assert headers[1] == "score"
        assert headers[2] == "meta"
        assert headers[3] == "created_at"


class TestExportScoresEmptyActivity:
    """When no scores exist, the CSV must contain only the header row."""

    def test_empty_activity_returns_header_only(self):
        from app.services import exportScores
        with patch("app.services.supabase_client", _build_mock([])):
            result = exportScores(INSTRUCTOR_EMAIL, INSTRUCTOR_PASS, COURSE_ID, ACTIVITY_NO)
        reader = csv.reader(io.StringIO(result["csv"]))
        rows = list(reader)
        assert len(rows) == 1  # header only
        assert rows[0] == EXPECTED_HEADERS


class TestExportScoresRowContent:
    """Validate that score rows contain correct data."""

    def test_single_student_row_count(self):
        from app.services import exportScores
        scores = [_make_score_row("alice@test.com", 1.0, "obj1", "2026-05-11T10:00:00")]
        with patch("app.services.supabase_client", _build_mock(scores)):
            result = exportScores(INSTRUCTOR_EMAIL, INSTRUCTOR_PASS, COURSE_ID, ACTIVITY_NO)
        reader = csv.reader(io.StringIO(result["csv"]))
        rows = list(reader)
        assert len(rows) == 2  # header + 1 data row

    def test_single_student_email_in_row(self):
        from app.services import exportScores
        scores = [_make_score_row("alice@test.com", 1.0, "obj1", "2026-05-11T10:00:00")]
        with patch("app.services.supabase_client", _build_mock(scores)):
            result = exportScores(INSTRUCTOR_EMAIL, INSTRUCTOR_PASS, COURSE_ID, ACTIVITY_NO)
        reader = csv.reader(io.StringIO(result["csv"]))
        next(reader)  # skip header
        data_row = next(reader)
        assert data_row[0] == "alice@test.com"

    def test_single_student_score_value(self):
        from app.services import exportScores
        scores = [_make_score_row("alice@test.com", 2.0, "", "2026-05-11T10:00:00")]
        with patch("app.services.supabase_client", _build_mock(scores)):
            result = exportScores(INSTRUCTOR_EMAIL, INSTRUCTOR_PASS, COURSE_ID, ACTIVITY_NO)
        reader = csv.reader(io.StringIO(result["csv"]))
        next(reader)
        data_row = next(reader)
        assert float(data_row[1]) == 2.0

    def test_multiple_students_row_count(self):
        from app.services import exportScores
        scores = [
            _make_score_row("alice@test.com", 1.0, "obj1", "2026-05-11T10:00:00"),
            _make_score_row("bob@test.com", 2.0, "obj2", "2026-05-11T10:05:00"),
            _make_score_row("carol@test.com", 3.0, "obj3", "2026-05-11T10:10:00"),
        ]
        with patch("app.services.supabase_client", _build_mock(scores)):
            result = exportScores(INSTRUCTOR_EMAIL, INSTRUCTOR_PASS, COURSE_ID, ACTIVITY_NO)
        reader = csv.reader(io.StringIO(result["csv"]))
        rows = list(reader)
        assert len(rows) == 4  # header + 3 data rows

    def test_multiple_students_each_on_own_line(self):
        from app.services import exportScores
        scores = [
            _make_score_row("alice@test.com", 1.0, "", "2026-05-11T10:00:00"),
            _make_score_row("bob@test.com", 1.0, "", "2026-05-11T10:05:00"),
        ]
        with patch("app.services.supabase_client", _build_mock(scores)):
            result = exportScores(INSTRUCTOR_EMAIL, INSTRUCTOR_PASS, COURSE_ID, ACTIVITY_NO)
        reader = csv.reader(io.StringIO(result["csv"]))
        next(reader)  # skip header
        emails = [row[0] for row in reader]
        assert "alice@test.com" in emails
        assert "bob@test.com" in emails

    def test_meta_field_preserved(self):
        from app.services import exportScores
        scores = [_make_score_row("alice@test.com", 1.0, "Objective achieved: OSI layer", "2026-05-11T10:00:00")]
        with patch("app.services.supabase_client", _build_mock(scores)):
            result = exportScores(INSTRUCTOR_EMAIL, INSTRUCTOR_PASS, COURSE_ID, ACTIVITY_NO)
        reader = csv.reader(io.StringIO(result["csv"]))
        next(reader)
        data_row = next(reader)
        assert data_row[2] == "Objective achieved: OSI layer"

    def test_created_at_field_preserved(self):
        from app.services import exportScores
        scores = [_make_score_row("alice@test.com", 1.0, "", "2026-05-11T10:00:00")]
        with patch("app.services.supabase_client", _build_mock(scores)):
            result = exportScores(INSTRUCTOR_EMAIL, INSTRUCTOR_PASS, COURSE_ID, ACTIVITY_NO)
        reader = csv.reader(io.StringIO(result["csv"]))
        next(reader)
        data_row = next(reader)
        assert data_row[3] == "2026-05-11T10:00:00"


class TestExportScoresAuthorization:
    """exportScores must reject unauthorized access."""

    def test_wrong_password_returns_error(self):
        from app.services import exportScores

        def table_side_effect(name):
            m = MagicMock()
            if name == "instructors":
                wrong = {**_make_instructor(), "password_hash": _hash("wrongpass")}
                m.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(data=wrong)
            return m

        mock_sb = MagicMock()
        mock_sb.table.side_effect = table_side_effect

        with patch("app.services.supabase_client", mock_sb):
            result = exportScores(INSTRUCTOR_EMAIL, INSTRUCTOR_PASS, COURSE_ID, ACTIVITY_NO)
        assert result["ok"] is False
        assert "error" in result

    def test_instructor_not_owner_returns_error(self):
        from app.services import exportScores

        def table_side_effect(name):
            m = MagicMock()
            if name == "instructors":
                m.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(data=_make_instructor())
            elif name == "courses":
                # Returns None → instructor does not own this course
                m.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(data=None)
            return m

        mock_sb = MagicMock()
        mock_sb.table.side_effect = table_side_effect

        with patch("app.services.supabase_client", mock_sb):
            result = exportScores(INSTRUCTOR_EMAIL, INSTRUCTOR_PASS, COURSE_ID, ACTIVITY_NO)
        assert result["ok"] is False
        assert "error" in result

    def test_no_credentials_returns_error(self):
        from app.services import exportScores
        with patch("app.services.supabase_client", MagicMock()):
            result = exportScores(INSTRUCTOR_EMAIL, None, COURSE_ID, ACTIVITY_NO)
        assert result["ok"] is False
