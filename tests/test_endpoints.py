"""
Endpoint (API) tests for US-A and US-B: Google Auth
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch, MagicMock

client = TestClient(app)

INSTRUCTOR_EMAIL = "test@mef.edu.tr"
STUDENT_EMAIL = "test@mef.edu.tr"


def _make_instructor():
    return {
        "id": "uuid",
        "email": INSTRUCTOR_EMAIL,
        "password_hash": None,
    }


def _make_student():
    return {
        "id": "uuid",
        "email": STUDENT_EMAIL,
        "password_hash": None,
    }


def test_instructor_login_endpoint_google_success():
    """Test POST /instructor/login with valid Google token."""
    with patch("app.services._extract_google_email", return_value=("test@mef.edu.tr", None)), \
         patch("app.services.supabase_client") as mock_sb:
        
        m = MagicMock()
        m.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(data=_make_instructor())
        mock_sb.table.return_value = m

        response = client.post("/instructor/login", json={
            "email": INSTRUCTOR_EMAIL,
            "token": "valid_token"
        })

    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert "instructor" in data
    assert data["instructor"]["email"] == INSTRUCTOR_EMAIL


def test_student_login_endpoint_google_success():
    """Test POST /student/login with valid Google token."""
    with patch("app.services._extract_google_email", return_value=("test@mef.edu.tr", None)), \
         patch("app.services.supabase_client") as mock_sb:
        
        m = MagicMock()
        m.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(data=_make_student())
        mock_sb.table.return_value = m

        response = client.post("/student/login", json={
            "email": STUDENT_EMAIL,
            "token": "valid_token"
        })

    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert "student" in data
    assert data["student"]["email"] == STUDENT_EMAIL
