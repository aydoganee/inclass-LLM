# Sprint 1 Planning Record

**Team:** Group 12  
**Date:** 2026-04-15  
**Duration:** ~1.5 hours  
**Attendees:** Emin Altay Aydoğan, Mustafa İlker Çınar, Baran Azabağaoğlu, Ayhan Azra Kervan, Oğuzhan Elmas  
**Facilitator:** Ayhan Azra Kervan

---

## Sprint Goal

Deliver a fully working InClass LLM Platform backend: implement all authentication, course and activity management, student access control, and the Socratic LLM tutoring flow with objective-based scoring — persisted in Supabase, accessible via FastAPI endpoints.

---

## Planning Poker — SP Estimates

| User Story | Estimates (per person) | Final SP | Notes |
|---|---|---|---|
| US-A: Instructor sign-in | 3, 3, 3, 3, 3 | 3 | Consensus |
| US-B: Student sign-in | 3, 3, 3, 3, 3 | 3 | Consensus |
| US-C: Role mapping | 5, 5, 8, 5, 5 | 5 | One outlier discussed, agreed 5 |
| US-D: List courses | 3, 3, 3, 3, 3 | 3 | Consensus |
| US-E: List activities | 3, 3, 3, 3, 3 | 3 | Consensus |
| US-F: Create activity | 5, 5, 5, 8, 5 | 5 | Outlier explained complexity of duplicate-check |
| US-G: Update activity | 5, 5, 5, 5, 5 | 5 | Consensus |
| US-H: Start/end activity | 5, 5, 5, 5, 5 | 5 | Consensus |
| US-I: Student access control | 5, 5, 5, 5, 5 | 5 | Consensus |
| US-J: Tutoring flow | 8, 8, 8, 13, 8 | 8 | LLM integration adds complexity; agreed 8 |
| US-K: Scoring | 8, 8, 8, 8, 8 | 8 | Consensus |
| US-L: Manual grading | 5, 5, 5, 5, 5 | 5 | Consensus |
| US-M: Reset activity | 5, 5, 5, 5, 5 | 5 | Consensus |

**Total: 63 SP**

---

## Task Assignment

| Person | Assigned Stories | SP |
|---|---|---|
| Emin Altay Aydoğan | US-F, US-J | 13 |
| Mustafa İlker Çınar | US-A, US-B, US-C | 11 |
| Oğuzhan Elmas | US-G, US-H, US-I | 15 |
| Baran Azabağaoğlu | US-D, US-E, US-K | 14 |
| Ayhan Azra Kervan | US-L, US-M | 10 |

---

## Decisions Made

- Sprint 1 facilitator: Ayhan Azra Kervan
- All work done in Python + FastAPI + Supabase (as required by spec)
- OpenRouter API used for LLM integration (free tier)
- Branch naming: `feature/US-<ID>-<short-description>`
- Each story gets its own PR with at least one code review
- GitHub repo: `aydoganee/inclass-LLM`
