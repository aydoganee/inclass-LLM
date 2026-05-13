# Sprint 1 Review

**Team:** Group 12  
**Date:** 2026-05-06  
**Sprint:** Sprint 1 (2026-04-15 to 2026-05-06)  
**Facilitator:** Ayhan Azra Kervan  
**Attendees:** Emin Altay Aydoğan, Mustafa İlker Çınar, Baran Azabağaoğlu, Ayhan Azra Kervan, Oğuzhan Elmas

---

## Sprint Goal Review

**Sprint Goal:** "Deliver a fully working InClass LLM Platform backend with all authentication, activity management, student access control, and Socratic LLM tutoring flow with objective-based scoring."

**Outcome:** Sprint Goal ACHIEVED ✓

---

## Completed Items

| Story | Description | SP | Status |
|-------|-------------|-----|--------|
| US-A | Instructor sign-in (password + Google token) | 3 | Done |
| US-B | Student sign-in (password + Google token) | 3 | Done |
| US-C | Role mapping and server-side auth enforcement | 5 | Done |
| US-D | Instructor lists assigned courses | 3 | Done |
| US-E | Instructor lists activities ordered by activity_no | 3 | Done |
| US-F | Instructor creates activity with duplicate check | 5 | Done |
| US-G | Instructor updates activity text and objectives | 5 | Done |
| US-H | Instructor starts and ends activity (ACTIVE/ENDED) | 5 | Done |
| US-I | Student access to ACTIVE only; objectives hidden | 5 | Done |
| US-J | Socratic tutoring flow, one question per turn | 8 | Done |
| US-K | +1 score per first objective; mini-lesson; celebration | 8 | Done |
| US-L | Instructor manual grading with logging | 5 | Done |
| US-M | Instructor reset activity (delete scores + ENDED) | 5 | Done |

**Total SP Completed: 63 / 63**

---

## Demo Summary

The following flows were demonstrated manually via Postman:

1. Instructor login → create activity → start activity
2. Student login → get activity (objectives hidden) → tutoring conversation → score increments
3. Instructor export scores → CSV with student_email, score, meta, created_at
4. Instructor reset activity → scores deleted, status ENDED

---

## Notes

- No unplanned items were added to Sprint 1
- All 13 PRs merged with at least one review comment
- `sprint-1` git tag to be created before Sprint 2 planning
- Sprint 2 will focus on testing, API compliance, frontend UI, and submission
