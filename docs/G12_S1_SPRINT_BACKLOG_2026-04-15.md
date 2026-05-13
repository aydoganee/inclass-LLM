# Sprint 1 Backlog — Task Level Breakdown

**Team:** Group 12  
**Sprint 1 Period:** 2026-04-15 to 2026-05-06  
**Scrum Master:** Ayhan Azra Kervan

---

## Sprint Backlog (Task Level)

| Task ID | User Story | Task Description | Assignee | SP | Status |
|---------|-----------|-----------------|----------|-----|--------|
| US-J-1 | US-J | Set up OpenRouter API client and test LLM call | Emin Altay Aydoğan | 2 | Done |
| US-J-2 | US-J | Implement Socratic system prompt with objective detection markers | Emin Altay Aydoğan | 3 | Done |
| US-J-3 | US-J | Implement student_progress table load/save | Emin Altay Aydoğan | 3 | Done |
| US-F-1 | US-F | Implement createActivity with auto activity_no and duplicate check | Emin Altay Aydoğan | 3 | Done |
| US-F-2 | US-F | Add `/instructor/create-activity` route to main.py | Emin Altay Aydoğan | 2 | Done |
| US-A-1 | US-A | Implement instructorLogin with password and token auth | Mustafa İlker Çınar | 1.5 | Done |
| US-B-1 | US-B | Implement studentLogin with password and token auth | Mustafa İlker Çınar | 1.5 | Done |
| US-C-1 | US-C | Implement Google token verification via google-auth library | Mustafa İlker Çınar | 2 | Done |
| US-C-2 | US-C | Add server-side role check helpers (_auth_instructor, _auth_student) | Mustafa İlker Çınar | 3 | Done |
| US-G-1 | US-G | Implement updateActivity with allowed-field check | Oğuzhan Elmas | 2 | Done |
| US-G-2 | US-G | Add `/instructor/update-activity` route | Oğuzhan Elmas | 1 | Done |
| US-H-1 | US-H | Implement startActivity and endActivity | Oğuzhan Elmas | 2 | Done |
| US-H-2 | US-H | Add `/instructor/start-activity` and `/instructor/end-activity` routes | Oğuzhan Elmas | 1 | Done |
| US-I-1 | US-I | Implement getActivity with status check (ACTIVE only) | Oğuzhan Elmas | 2 | Done |
| US-I-2 | US-I | Strip learning_objectives from response to student | Oğuzhan Elmas | 1 | Done |
| US-K-1 | US-K | Implement objective detection via JSON marker parsing | Baran Azabağaoğlu | 3 | Done |
| US-K-2 | US-K | Implement logScore with duplicate prevention | Baran Azabağaoğlu | 2 | Done |
| US-K-3 | US-K | Add mini-lesson and celebration message generation | Baran Azabağaoğlu | 3 | Done |
| US-D-1 | US-D | Implement listMyCourses with instructor auth | Baran Azabağaoğlu | 2 | Done |
| US-E-1 | US-E | Implement listActivities ordered by activity_no | Baran Azabağaoğlu | 2 | Done |
| US-L-1 | US-L | Implement manual grade endpoint (update score record) | Ayhan Azra Kervan | 3 | Done |
| US-M-1 | US-M | Implement resetActivity (delete scores + set ENDED) | Ayhan Azra Kervan | 2 | Done |
| US-M-2 | US-M | Add `/instructor/reset-activity` route | Ayhan Azra Kervan | 1 | Done |
| INFRA-1 | — | Set up Supabase project, create all tables, set RLS policies | All | 2 | Done |
| INFRA-2 | — | Set up GitHub repo, branch protection, grant instructor access | All | 1 | Done |

---

## Notes

- All tasks completed by 2026-04-25 based on git commit history
- US-J semantic fallback for objective detection added as unplanned enhancement (2026-05-07 in Sprint 2)
