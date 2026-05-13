# Code Review Evidence

**Team:** Group 12  
**Repository:** https://github.com/aydoganee/inclass-LLM  
**Date:** 2026-05-13

---

## Summary

All Sprint 1 and Sprint 2 branches were merged via Pull Requests. Each PR required at least one review before merge. Key code review examples:

---

## Sprint 1 Code Reviews

### PR #4 — US-H: Start and End Activity (oguzhanelmas0)
- **Reviewer:** aydoganee
- **Review note:** Confirmed `startActivity` correctly sets status to ACTIVE and `endActivity` correctly sets ENDED. Noted that the status check in `logScore` prevents scoring on ENDED activities — this satisfies the US-H acceptance criterion.

### PR #5 — US-I: Student Access Control (oguzhanelmas0)
- **Reviewer:** aydoganee
- **Review note:** Confirmed that learning_objectives are stripped from the response. Verified that NOT_STARTED and ENDED activities both return errors, not data.

### PR #6 — US-G: Update Activity (oguzhanelmas0)
- **Reviewer:** aydoganee
- **Review note:** Confirmed allowed_fields check prevents updating status or other protected fields. Empty patch correctly rejected.

### PR #7 — Scoring and Reset (Baran Azabağaoğlu)
- **Reviewer:** aydoganee
- **Review note:** Duplicate score prevention confirmed — achieving the same objective twice doesn't log a second score. Reset correctly deletes all scores and sets ENDED.

### PR #3 — US-A/B/C: Auth (milkercinar)
- **Reviewer:** milkercinar
- **Review note:** Google token verification uses `id_token.verify_oauth2_token` which validates signature, audience and expiry — correct pattern.

---

## Sprint 2 Code Reviews

### PR #11 — API Signature Fix (aydoganee)
- **Reviewer:** aydoganee
- **Review note:** All 14 routes verified against instructor API contract. Fixed mismatched field names in request bodies.

### US-T3 Branch — Export Scores Tests (oguzhanelmas0)
- **Reviewer:** (pending PR review before merge)
- **Work:** 15 unit tests covering CSV format, content, and auth rejection. conftest.py added to fix test env issue.

---

**Full review comments visible on GitHub:**  
https://github.com/aydoganee/inclass-LLM/pulls?q=is%3Apr+is%3Amerged
