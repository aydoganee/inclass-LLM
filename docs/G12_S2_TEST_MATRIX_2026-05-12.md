# Acceptance Criteria & Test Matrix — Sprint 2

**Team:** Group 12  
**Date:** 2026-05-12  

---

## US-T3: Export Scores — CSV Validation

| # | Acceptance Criterion | Test File | Test Name | Result |
|---|---------------------|-----------|-----------|--------|
| 1 | CSV header row is exactly: `student_email,score,meta,created_at` | test_export_scores.py | test_csv_headers_correct | PASS |
| 2 | Column order: student_email first, created_at last | test_export_scores.py | test_csv_header_order | PASS |
| 3 | Empty activity returns header-only (no data rows) | test_export_scores.py | test_empty_activity_returns_header_only | PASS |
| 4 | Single student → 1 data row + header = 2 total rows | test_export_scores.py | test_single_student_row_count | PASS |
| 5 | Student email appears correctly in first column | test_export_scores.py | test_single_student_email_in_row | PASS |
| 6 | Score value preserved as float in second column | test_export_scores.py | test_single_student_score_value | PASS |
| 7 | Multiple students each appear on their own line | test_export_scores.py | test_multiple_students_each_on_own_line | PASS |
| 8 | Multiple students → correct total row count | test_export_scores.py | test_multiple_students_row_count | PASS |
| 9 | Meta field content preserved unchanged | test_export_scores.py | test_meta_field_preserved | PASS |
| 10 | created_at timestamp preserved unchanged | test_export_scores.py | test_created_at_field_preserved | PASS |
| 11 | Wrong instructor password → ok: false, error present | test_export_scores.py | test_wrong_password_returns_error | PASS |
| 12 | Instructor who doesn't own course → ok: false | test_export_scores.py | test_instructor_not_owner_returns_error | PASS |
| 13 | No credentials → ok: false | test_export_scores.py | test_no_credentials_returns_error | PASS |
| 14 | Response contains "ok": true on success | test_export_scores.py | test_returns_ok_true | PASS |
| 15 | Response contains "csv" key on success | test_export_scores.py | test_csv_key_present | PASS |

**Result: 15/15 PASS**

---

## US-H: Start / End Activity

| # | Acceptance Criterion | Test File | Test Name | Result |
|---|---------------------|-----------|-----------|--------|
| 1 | startActivity sets status to ACTIVE | test_us_h.py | test_start_activity_success | PASS |
| 2 | Wrong password on startActivity → error | test_us_h.py | test_start_activity_wrong_password | PASS |
| 3 | Non-owner instructor on startActivity → error | test_us_h.py | test_start_activity_not_owner | PASS |
| 4 | Non-existent activity on startActivity → error | test_us_h.py | test_start_activity_not_found | PASS |
| 5 | endActivity sets status to ENDED | test_us_h.py | test_end_activity_success | PASS |
| 6 | ENDED activity blocks new score logging | test_us_h.py | test_ended_activity_rejects_score_log | PASS |
| 7 | Wrong instructor on endActivity → error | test_us_h.py | test_end_activity_wrong_instructor | PASS |

**Result: 7/7 PASS**

---

## US-I: Student Access Control

| # | Acceptance Criterion | Test File | Test Name | Result |
|---|---------------------|-----------|-----------|--------|
| 1 | NOT_STARTED activity blocked for student | test_us_i.py | test_not_started_activity_is_blocked | PASS |
| 2 | ACTIVE activity returns text, hides learning_objectives | test_us_i.py | test_active_activity_returns_text_without_objectives | PASS |
| 3 | ENDED activity blocked for student | test_us_i.py | test_ended_activity_is_blocked | PASS |
| 4 | Unenrolled student rejected | test_us_i.py | test_unenrolled_student_is_rejected | PASS |
| 5 | Invalid student credentials rejected | test_us_i.py | test_invalid_student_credentials | PASS |

**Result: 5/5 PASS**

---

## US-G: Update Activity

| # | Acceptance Criterion | Test File | Test Name | Result |
|---|---------------------|-----------|-----------|--------|
| 1 | activity_text can be updated | test_us_g.py | test_update_activity_text_success | PASS |
| 2 | learning_objectives can be updated | test_us_g.py | test_update_learning_objectives_success | PASS |
| 3 | Empty patch rejected with error | test_us_g.py | test_empty_patch_is_rejected | PASS |
| 4 | Disallowed fields (e.g. status) rejected | test_us_g.py | test_disallowed_fields_are_rejected | PASS |
| 5 | Non-existent activity returns error | test_us_g.py | test_nonexistent_activity_returns_error | PASS |
| 6 | Non-owner instructor rejected | test_us_g.py | test_unauthorized_instructor_is_rejected | PASS |

**Result: 6/6 PASS**

---

## Summary

| User Story | Tests | Pass | Fail |
|-----------|-------|------|------|
| US-T3 Export Scores CSV | 15 | 15 | 0 |
| US-H Start/End Activity | 7 | 7 | 0 |
| US-I Student Access | 5 | 5 | 0 |
| US-G Update Activity | 6 | 6 | 0 |
| **Total** | **33** | **33** | **0** |

Run command: `.venv/bin/python -m pytest tests/ -v`
