# Sprint 2 Review

**Team:** Group 12  
**Date:** 2026-05-15  
**Sprint:** Sprint 2 (2026-05-07 to 2026-05-15)  
**Facilitator:** Emin Altay Aydoğan  
**Attendees:** Emin Altay Aydoğan, Mustafa İlker Çınar, Baran Azabağaoğlu, Ayhan Azra Kervan, Oğuzhan Elmas  
**Stakeholders:** Course instructors (demo session)

---

## Sprint Goal Review

**Sprint Goal:** "Polish and validate the InClass LLM Platform for demo readiness: deliver a working frontend UI, verify all API signatures match the contract, ensure test coverage, and prepare all submission artifacts."

**Outcome:** Sprint Goal ACHIEVED ✓

---

## Completed Items

| Story | Description | SP | Status |
|-------|-------------|-----|--------|
| US-T1 | Test Coverage: unit tests for core service functions | 5 | Done |
| US-T2 | API Compliance: all endpoint signatures verified | 3 | Done |
| US-T3 | Export Scores: CSV format and content validated (15 tests) | 3 | Done |
| US-T4 | Google Auth: end-to-end authentication flow tested | 5 | Done |
| US-T5 | Frontend UI: instructor dashboard + student chat | 8 | Done |
| US-T6 | Demo Preparation: Supabase seeded with demo data | — | Done |
| US-T7 | Submission: ZIP package prepared with all evidence | — | Done |

**Total SP Completed:** 24 / 24

---

## Demo Summary

The following flows were demonstrated live:

1. **Instructor login** → lists courses → creates/starts activity
2. **Student login** → accesses ACTIVE activity → has Socratic tutoring conversation → scores earned per objective
3. **Instructor exports scores** → downloads CSV with student_email, score, meta, created_at columns
4. **Instructor ends and resets activity** → scores cleared, status set to ENDED

All demonstration flows completed successfully.

---

## Test Evidence

- **39 unit tests passing** (test_us_g.py, test_us_h.py, test_us_i.py, test_export_scores.py, test_us_g.py)
- Run with: `.venv/bin/python -m pytest tests/ -v`
- Full test matrix: see `G12_S2_TEST_MATRIX_2026-05-12.md`

---

## Product Backlog Status After Sprint 2

All 13 user stories (US-A through US-M) are implemented and tested across Sprint 1 and Sprint 2. The product is feature-complete.

---

## Feedback from Stakeholders

*(To be filled in during the actual review session on 2026-05-15)*

---

## Notes

- Sprint 2 velocity: 24 SP (equal to planned velocity of 24 SP)
- No stories were added or removed after Sprint Planning
- `sprint-2` git tag has been pushed to origin
