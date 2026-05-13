# Sprint 1 Goal

**Team:** Group 12  
**Sprint 1 Period:** 2026-04-15 to 2026-05-06  
**Scrum Facilitator (Sprint 1):** Ayhan Azra Kervan

---

## Sprint Goal Statement

Deliver a fully working InClass LLM Platform backend: implement all authentication, course and activity management, student access control, and the Socratic LLM tutoring flow with objective-based scoring — persisted in Supabase, accessible via FastAPI endpoints.

---

## Sprint 1 Scope

| User Story | Description | SP | Assignee |
|---|---|---|---|
| US-A | Instructor sign-in with federated auth | 3 | Mustafa İlker Çınar |
| US-B | Student sign-in with federated auth | 3 | Mustafa İlker Çınar |
| US-C | Map authenticated users to roles and course access | 5 | Mustafa İlker Çınar |
| US-D | Instructor lists only assigned courses | 3 | Baran Azabağaoğlu |
| US-E | Instructor lists activities in course | 3 | Baran Azabağaoğlu |
| US-F | Instructor creates activity with text and objectives | 5 | Emin Altay Aydoğan |
| US-G | Instructor updates activity | 5 | Oğuzhan Elmas |
| US-H | Instructor starts and ends activity | 5 | Oğuzhan Elmas |
| US-I | Student access control (ACTIVE only, objectives hidden) | 5 | Oğuzhan Elmas |
| US-J | Student tutoring flow (Socratic LLM, one question at a time) | 8 | Emin Altay Aydoğan |
| US-K | Objective-based scoring (+1, no repeat, mini-lesson, celebration) | 8 | Baran Azabağaoğlu |
| US-L | Instructor manual grading | 5 | Ayhan Azra Kervan |
| US-M | Instructor reset activity | 5 | Ayhan Azra Kervan |

**Total: 63 SP**

---

## Definition of Done (Sprint 1)

- All 13 user story endpoints implemented and tested manually
- Supabase schema set up and all CRUD operations working
- FastAPI routes match the instructor-provided contract
- Code reviewed via GitHub PR before merge to main
- `sprint-1` git tag created and pushed
