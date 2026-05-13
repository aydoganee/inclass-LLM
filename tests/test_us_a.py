"""
Tests for US-A: Instructor Authentication with Google Sign-In
"""

import pytest
from unittest.mock import patch, MagicMock

INSTRUCTOR_EMAIL = "test@mef.edu.tr"


def _make_instructor():
    return {
        "id": "uuid",
        "email": INSTRUCTOR_EMAIL,
        "password_hash": None,
    }


def test_instructor_login_google_success():
    """Valid federated sign-in returns successful authentication."""
    from app.services import instructorLogin

    instructor = _make_instructor()

    # Mock _extract_google_email to return success and mock supabase client
    with patch("app.services._extract_google_email", return_value=("test@mef.edu.tr", None)), \
         patch("app.services.supabase_client") as mock_sb:
        
        m = MagicMock()
        m.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(data=instructor)
        mock_sb.table.return_value = m

        result = instructorLogin(email=INSTRUCTOR_EMAIL, password=None, token="valid_token")

    assert result["ok"] is True
    assert "instructor" in result
    assert result["instructor"]["email"] == INSTRUCTOR_EMAIL


def test_instructor_login_google_invalid_token():
    """Invalid Google token must be rejected."""
    from app.services import instructorLogin

    with patch("app.services._extract_google_email", side_effect=Exception("Invalid token")):
        result = instructorLogin(email=INSTRUCTOR_EMAIL, password=None, token="invalid_token")

    assert result["ok"] is False
    assert result["error"] == "Invalid token"


def test_instructor_login_google_email_mismatch():
    """Token email mismatch must be rejected."""
    from app.services import instructorLogin

    with patch("app.services._extract_google_email", side_effect=Exception("Token email mismatch")):
        result = instructorLogin(email="other@test.com", password=None, token="valid_token_for_instructor")

    assert result["ok"] is False
    assert result["error"] == "Token email mismatch"


def test_instructor_login_google_unregistered_instructor():
    """Identity not mapped to an instructor account returns a clear error."""
    from app.services import instructorLogin

    with patch("app.services._extract_google_email", return_value=("not_registered@test.com", None)), \
         patch("app.services.supabase_client") as mock_sb:
        
        m = MagicMock()
        # Simulate not found
        m.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(data=None)
        mock_sb.table.return_value = m

        result = instructorLogin(email="not_registered@test.com", password=None, token="valid_token")

    assert result["ok"] is False
    assert result["error"] == "Instructor not found"
