from unittest.mock import MagicMock, patch
import pytest
from app.services import logScore, listActivities, resetActivity

# Mock veriler
MOCK_STUDENT = {"id": "std-123", "email": "baran@mef.edu.tr", "password_hash": "hashed_pass"}
MOCK_INSTRUCTOR = {"id": "ins-456", "email": "hoca@mef.edu.tr", "password_hash": "hashed_pass"}
MOCK_COURSE_ID = "course-eng-101"
MOCK_ACTIVITY = {
    "id": "act-789",
    "course_id": MOCK_COURSE_ID,
    "activity_no": 1,
    "status": "ACTIVE",
    "activity_text": "Sample Test",
    "learning_objectives": ["Obj 1"]
}


@pytest.fixture
def mock_auth_student():
    with patch("app.services._auth_student") as mock:
        mock.return_value = (MOCK_STUDENT, None)
        yield mock


@pytest.fixture
def mock_auth_instructor():
    with patch("app.services._auth_instructor") as mock:
        mock.return_value = (MOCK_INSTRUCTOR, None)
        yield mock


@pytest.fixture
def mock_enrollment():
    with patch("app.services._student_enrolled_in_course") as mock:
        mock.return_value = True
        yield mock


@pytest.fixture
def mock_ownership():
    with patch("app.services._instructor_owns_course") as mock:
        mock.return_value = True
        yield mock


@pytest.fixture
def mock_get_activity():
    with patch("app.services._get_activity") as mock:
        mock.return_value = (MOCK_ACTIVITY, None)
        yield mock


# ---------------------------------------------------------------------------
# US-K: logScore Testleri
# ---------------------------------------------------------------------------

@patch("app.services.supabase_client")
def test_log_score_success_first_attempt(mock_supabase, mock_auth_student, mock_enrollment, mock_get_activity):
    """Kriter: İlk başarımda skor başarıyla loglanmalı ve +1 puan eklenmeli."""
    query_chain = MagicMock()
    query_chain.select.return_value = query_chain
    query_chain.eq.return_value = query_chain
    query_chain.execute.return_value = MagicMock(data=[])

    insert_chain = MagicMock()

    mock_scores_table = MagicMock()
    mock_scores_table.select.return_value = query_chain
    mock_scores_table.insert.return_value = insert_chain

    mock_supabase.table.return_value = mock_scores_table

    res = logScore("baran@mef.edu.tr", "password", MOCK_COURSE_ID, 1, score=1.0, meta="Objective achieved: Obj 1")

    assert res["ok"] is True
    assert mock_scores_table.insert.called is True


@patch("app.services.supabase_client")
def test_log_score_duplicate_prevention(mock_supabase, mock_auth_student, mock_enrollment, mock_get_activity):
    """Kriter: Aynı hedef (meta) tekrar gönderildiğinde yeni skor eklenmemeli (Duplicate prevention)."""
    query_chain = MagicMock()
    query_chain.select.return_value = query_chain
    query_chain.eq.return_value = query_chain
    query_chain.execute.return_value = MagicMock(data=[{"id": "score-999"}])

    mock_scores_table = MagicMock()
    mock_scores_table.select.return_value = query_chain

    mock_supabase.table.return_value = mock_scores_table

    res = logScore("baran@mef.edu.tr", "password", MOCK_COURSE_ID, 1, score=1.0, meta="Objective achieved: Obj 1")

    assert res["ok"] is True
    assert "not duplicated" in res["message"]
    assert mock_scores_table.insert.called is False


def test_log_score_fails_on_inactive_activity(mock_auth_student, mock_enrollment):
    """Kriter: Aktivite ACTIVE değilse skor kaydedilmemeli."""
    inactive_activity = MOCK_ACTIVITY.copy()
    inactive_activity["status"] = "ENDED"

    with patch("app.services._get_activity", return_value=(inactive_activity, None)):
        res = logScore("baran@mef.edu.tr", "password", MOCK_COURSE_ID, 1, score=1.0)
        assert res["ok"] is False
        assert "not active" in res["error"]


# ---------------------------------------------------------------------------
# US-E: listActivities Testleri
# ---------------------------------------------------------------------------

@patch("app.services.supabase_client")
def test_list_activities_success(mock_supabase, mock_auth_instructor, mock_ownership):
    """Kriter: Eğitmenin dersine ait aktiviteler listelenmeli."""
    mock_supabase.table().select().eq().order().execute.return_value.data = [MOCK_ACTIVITY]

    res = listActivities("hoca@mef.edu.tr", "password", MOCK_COURSE_ID)

    assert res["ok"] is True
    assert len(res["activities"]) == 1
    assert res["activities"][0]["activity_no"] == 1


# ---------------------------------------------------------------------------
# US-M: resetActivity Testleri
# ---------------------------------------------------------------------------

@patch("app.services.supabase_client")
def test_reset_activity_success(mock_supabase, mock_auth_instructor, mock_ownership, mock_get_activity):
    """Kriter: Aktivite resetlendiğinde skorlar silinmeli ve durumu ENDED yapılmalı."""
    res = resetActivity("hoca@mef.edu.tr", "password", MOCK_COURSE_ID, 1)

    assert res["ok"] is True
    assert mock_supabase.table().delete.called is True
    assert mock_supabase.table().update.called is True