"""
Tests for US-B: Student Authentication with Google Sign-In
"""

import pytest
from unittest.mock import patch, MagicMock

STUDENT_EMAIL = "student@test.com"


def _make_student():
    return {
        "id": "std-1",
        "email": STUDENT_EMAIL,
        "password_hash": "dummy_hash",
    }


def test_student_login_google_success():
    """Valid federated sign-in returns successful authentication."""
    from app.services import studentLogin

    student = _make_student()

    with patch("app.services._verify_google_token", return_value=(True, None)), \
         patch("app.services.supabase_client") as mock_sb:
        
        m = MagicMock()
        m.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(data=student)
        mock_sb.table.return_value = m

        result = studentLogin(email=STUDENT_EMAIL, password=None, token="valid_token")

    assert result["ok"] is True
    assert "student" in result
    assert result["student"]["email"] == STUDENT_EMAIL


def test_student_login_google_invalid_token():
    """Invalid Google token must be rejected."""
    from app.services import studentLogin

    with patch("app.services._verify_google_token", return_value=(False, "Invalid token")):
        result = studentLogin(email=STUDENT_EMAIL, password=None, token="invalid_token")

    assert result["ok"] is False
    assert result["error"] == "Invalid token"


def test_student_login_google_email_mismatch():
    """Token email mismatch must be rejected."""
    from app.services import studentLogin

    with patch("app.services._verify_google_token", return_value=(False, "Token email mismatch")):
        result = studentLogin(email="other@test.com", password=None, token="valid_token_for_student")

    assert result["ok"] is False
    assert result["error"] == "Token email mismatch"


def test_student_login_google_unregistered_student():
    """Identity not mapped to a student account returns a clear error."""
    from app.services import studentLogin

    with patch("app.services._verify_google_token", return_value=(True, None)), \
         patch("app.services.supabase_client") as mock_sb:
        
        m = MagicMock()
        m.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(data=None)
        mock_sb.table.return_value = m

        result = studentLogin(email="not_registered@test.com", password=None, token="valid_token")

    assert result["ok"] is False
    assert result["error"] == "Student not found"
