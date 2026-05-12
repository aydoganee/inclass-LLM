# Sprint 2 Backlog — Task Level Breakdown

**Team:** Group 12  
**Sprint 2 Period:** 2026-05-07 to 2026-05-15  
**Scrum Master:** Emin Altay Aydoğan

---

## Sprint Backlog (Task Level)

| Task ID | User Story | Task Description | Assignee | SP | Status |
|---------|-----------|-----------------|----------|-----|--------|
| US-T1-1 | US-T1 | Write unit tests for studentLogin and instructorLogin | Oğuzhan Elmas | 1 | Done |
| US-T1-2 | US-T1 | Write unit tests for createActivity and updateActivity | Oğuzhan Elmas | 1 | Done |
| US-T1-3 | US-T1 | Write unit tests for startActivity and endActivity | Oğuzhan Elmas | 1 | Done |
| US-T1-4 | US-T1 | Write unit tests for getActivity (student access control) | Oğuzhan Elmas | 1 | Done |
| US-T1-5 | US-T1 | Add conftest.py to fix env-var import issue for all tests | Oğuzhan Elmas | 1 | Done |
| US-T2-1 | US-T2 | Compare all API route signatures against contract | Mustafa İlker Çınar | 1 | Done |
| US-T2-2 | US-T2 | Fix any mismatched endpoint signatures | Mustafa İlker Çınar | 2 | Done |
| US-T3-1 | US-T3 | Read and analyse existing exportScores function | Oğuzhan Elmas | 0.5 | Done |
| US-T3-2 | US-T3 | Write tests for CSV header correctness | Oğuzhan Elmas | 1 | Done |
| US-T3-3 | US-T3 | Write tests for empty activity (header-only row) | Oğuzhan Elmas | 0.5 | Done |
| US-T3-4 | US-T3 | Write tests for multi-student row content & count | Oğuzhan Elmas | 0.5 | Done |
| US-T3-5 | US-T3 | Write tests for authorization rejection | Oğuzhan Elmas | 0.5 | Done |
| US-T4-1 | US-T4 | Set up Google OAuth test environment | Mustafa İlker Çınar | 2 | In Progress |
| US-T4-2 | US-T4 | Implement and test token verification end-to-end | Mustafa İlker Çınar | 3 | In Progress |
| US-T5-1 | US-T5 | Design HTML/JS layout for instructor dashboard | Emin Altay Aydoğan | 2 | In Progress |
| US-T5-2 | US-T5 | Implement student chat UI | Emin Altay Aydoğan | 3 | In Progress |
| US-T5-3 | US-T5 | Connect UI to FastAPI endpoints | Emin Altay Aydoğan | 3 | In Progress |
| US-T6-1 | US-T6 | Write idempotent seed_demo_data.py script | Oğuzhan Elmas | 1 | Done |
| US-T6-2 | US-T6 | Run seed script against real Supabase, verify data | Tüm Ekip | 1 | In Progress |
| US-T7-1 | US-T7 | Create REPO_INFO.txt | Oğuzhan Elmas | 0.5 | Done |
| US-T7-2 | US-T7 | Write prepare_submission.py (ZIP builder + checklist) | Oğuzhan Elmas | 1 | Done |
| US-T7-3 | US-T7 | Collect all Sprint 2 Scrum evidence files | Tüm Ekip | 1 | In Progress |
| US-T7-4 | US-T7 | Collect all Sprint 1 Scrum evidence files | Tüm Ekip | 1 | In Progress |
| US-T7-5 | US-T7 | Build and verify final ZIP package | Tüm Ekip | 0.5 | Not Started |
| US-T7-6 | US-T7 | Create and push sprint-2 git tag | Oğuzhan Elmas | 0.5 | Not Started |

---

## Notes

- US-T6 and US-T7 have no fixed SP as they are team-wide coordination tasks
- US-T1 tasks (test_us_g.py, test_us_h.py, test_us_i.py) were completed and merged to main
- conftest.py (US-T1-5) also fixes the test import issue that was blocking all existing tests
