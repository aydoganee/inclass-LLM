# Sprint 1 Goal

**Team:** Group 12  
**Sprint 1 Period:** 2026-04-15 to 2026-05-03  
**Scrum Facilitator (Sprint 1):** Ayhan Azra Kervan

---

## Sprint Goal Statement

Deliver a working backend with all core endpoints, database schema, and a functional AI-powered tutoring flow with objective-based scoring so that the platform can be demonstrated end-to-end.

---

## Sprint 1 Scope

| User Story | Description | SP | Assignee |
|---|---|---|---|
| US-A | Instructor Google Auth | 3 | Mustafa İlker Çınar |
| US-B | Student Google Auth | 3 | Mustafa İlker Çınar |
| US-C | Role/Course Mapping | 5 | Mustafa İlker Çınar |
| US-D | List My Courses | 3 | Ayhan Azra Kervan |
| US-E | List Activities | 3 | Baran Azabağaoğlu |
| US-F | Create Activity | 5 | Emin Altay Aydoğan |
| US-G | Update Activity | 5 | Oğuzhan Elmas / Ayhan Azra Kervan |
| US-H | Start/End Activity | 5 | Oğuzhan Elmas |
| US-I | Student Access Control | 5 | Oğuzhan Elmas |
| US-J | Tutoring Flow (LLM) | 8 | Emin Altay Aydoğan |
| US-K | Objective Scoring | 8 | Baran Azabağaoğlu |
| US-L | Manual Grading | 5 | Ayhan Azra Kervan |
| US-M | Reset Activity | 2 | Baran Azabağaoğlu |

**Total SP: 68**

---

## Task Assignment by Person

| Person | Assigned Stories | SP | Difficulty |
|---|---|---|---|
| Emin Altay Aydoğan | US-J, US-F | 13 | 🔴 Hard |
| Mustafa İlker Çınar | US-A, US-B, US-C | 11 | 🟠 Medium-Hard |
| Oğuzhan Elmas | US-H, US-I, US-G | 13 | 🟡 Medium |
| Baran Azabağaoğlu | US-K, US-E, US-M | 13 | 🟠 Medium-Hard |
| Ayhan Azra Kervan | US-L, US-G, US-D + Scrum artifacts | 11 | 🟢 Easy-Medium |

---

## Definition of Done (Sprint 1)

- [ ] Code is pushed to GitHub with a feature branch and merged via PR
- [ ] Endpoint returns correct response for happy path
- [ ] Endpoint returns `{"ok": false, "error": "..."}` for error cases
- [ ] Email + password authentication is validated on every call
- [ ] Supabase records are correctly created/updated/deleted
- [ ] Manually tested via Swagger UI
- [ ] ClickUp task moved to Completed

---

## Sprint 1 Outcome

All 13 user stories were implemented. The platform is fully functional end-to-end:
- All 17+ API endpoints are live and tested
- Supabase schema deployed with all required tables
- AI tutoring flow works with semantic objective detection
- Scoring, mini-lessons, and completion behavior verified
