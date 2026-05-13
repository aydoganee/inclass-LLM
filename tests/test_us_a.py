"""
Tests for US-A: Instructor Authentication with Google Sign-In
"""

import pytest
from unittest.mock import patch, MagicMock

INSTRUCTOR_EMAIL = "instructor@test.com"


def _make_instructor():
    return {
        "id": "inst-1",
        "email": INSTRUCTOR_EMAIL,
        "password_hash": "dummy_hash",
    }


def test_instructor_login_google_success():
    """Valid federated sign-in returns successful authentication."""
    from app.services import instructorLogin

    instructor = _make_instructor()

    # Mock _verify_google_token to return success and mock supabase client
    with patch("app.services._verify_google_token", return_value=(True, None)), \
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

    with patch("app.services._verify_google_token", return_value=(False, "Invalid token")):
        result = instructorLogin(email=INSTRUCTOR_EMAIL, password=None, token="invalid_token")

    assert result["ok"] is False
    assert result["error"] == "Invalid token"


def test_instructor_login_google_email_mismatch():
    """Token email mismatch must be rejected."""
    from app.services import instructorLogin

    with patch("app.services._verify_google_token", return_value=(False, "Token email mismatch")):
        result = instructorLogin(email="other@test.com", password=None, token="valid_token_for_instructor")

    assert result["ok"] is False
    assert result["error"] == "Token email mismatch"


def test_instructor_login_google_unregistered_instructor():
    """Identity not mapped to an instructor account returns a clear error."""
    from app.services import instructorLogin

    with patch("app.services._verify_google_token", return_value=(True, None)), \
         patch("app.services.supabase_client") as mock_sb:
        
        m = MagicMock()
        # Simulate not found
        m.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(data=None)
        mock_sb.table.return_value = m

        result = instructorLogin(email="not_registered@test.com", password=None, token="valid_token")

    assert result["ok"] is False
    assert result["error"] == "Instructor not found"
