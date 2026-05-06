# Sprint 2 Planning Record

**Team:** Group 12  
**Date:** 2026-05-07  
**Duration:** ~1 hour  
**Attendees:** Emin Altay Aydoğan, Mustafa İlker Çınar, Baran Azabağaoğlu, Ayhan Azra Kervan, Oğuzhan Elmas  
**Facilitator:** Emin Altay Aydoğan

---

## Sprint Goal

Polish and validate the InClass LLM Platform for demo readiness: deliver a working frontend UI, verify all API signatures match the contract, ensure test coverage, and prepare all submission artifacts.

---

## Planning Poker — SP Estimates

| User Story | Initial SP | Re-estimated SP | Notes |
|---|---|---|---|
| US-T1: Test Coverage | 5 | 5 | Unit tests for core services |
| US-T2: API Compliance | 3 | 3 | Signature verification |
| US-T3: Export Scores CSV | 3 | 3 | Format validation |
| US-T4: Google Auth E2E | 5 | 5 | End-to-end auth flow |
| US-T5: Frontend UI | 8 | 8 | Instructor + student interface |

**Total: 24 SP**

---

## Task Assignment

| Person | Assigned Stories | SP |
|---|---|---|
| Emin Altay Aydoğan | US-T5 | 8 |
| Mustafa İlker Çınar | US-T4, US-T2 | 8 |
| Oğuzhan Elmas | US-T1, US-T3 | 8 |
| Baran Azabağaoğlu | US-T6 (demo data) | - |
| Ayhan Azra Kervan | US-T7 (submission) | - |
| All | US-T6, US-T7 | shared |

---

## Decisions Made

- Sprint 2 facilitator: Emin Altay Aydoğan (different from Sprint 1 facilitator Ayhan Azra Kervan)
- Frontend will be built with HTML/JS served from FastAPI static files
- Demo date: 2026-05-15
- Supabase must have 2 instructors, 2 students, 2 courses for demo
- `sprint-2` tag to be created on last day before demo
