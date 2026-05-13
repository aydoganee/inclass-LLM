# Product Backlog — Initial

**Team:** Group 12  
**Date:** 2026-04-15 (Sprint 1 Planning)  
**Total Story Points:** 63 SP (product) + 24 SP (Sprint 2 testing) = 87 SP

---

## Product Backlog Items

| ID | User Story | Initial SP | Priority | Notes |
|----|-----------|-----------|----------|-------|
| US-A | Instructor sign-in with federated auth | 3 | High | Google OAuth or password |
| US-B | Student sign-in with federated auth | 3 | High | Google OAuth or password |
| US-C | Map authenticated users to roles and course access (server-side) | 5 | High | Role enforcement per request |
| US-D | Instructor lists only assigned courses | 3 | High | |
| US-E | Instructor lists activities in course with status | 3 | Medium | Ordered by activity_no |
| US-F | Instructor creates activity with text and objectives | 5 | High | Reject duplicate activity_no |
| US-G | Instructor updates activity text and objectives | 5 | Medium | Only allowed fields |
| US-H | Instructor starts (ACTIVE) and ends (ENDED) activity | 5 | High | ENDED blocks new scores |
| US-I | Student accesses only ACTIVE activities; objectives hidden | 5 | High | Enrollment check |
| US-J | Student submits answers; receives next Socratic question; progress stored | 8 | High | LLM via OpenRouter |
| US-K | Score +1 on first objective achievement; no repeat; mini-lesson; celebrate completion | 8 | High | logScore integration |
| US-L | Instructor manual grade for exceptions with logging | 5 | Medium | |
| US-M | Instructor resets activity: delete scores, set ENDED | 5 | Medium | Idempotent |

**Total Product SP: 63**

---

## Sprint 2 Testing Backlog (added at Sprint 2 planning on 2026-05-07)

| ID | Task | SP |
|----|------|----|
| US-T1 | Unit tests for core service functions | 5 |
| US-T2 | API compliance verification | 3 |
| US-T3 | Export scores CSV validation | 3 |
| US-T4 | Google Auth end-to-end test | 5 |
| US-T5 | Frontend UI | 8 |
| US-T6 | Demo data seeding | — |
| US-T7 | Submission package | — |

**Sprint 2 Testing SP: 24**
