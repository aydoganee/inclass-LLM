# Product Goal

**Team:** Group 12  
**Project:** InClass LLM Platform  
**Date Established:** 2026-04-15

---

## Product Goal Statement

Build a classroom activity system where instructors control in-class LLM-based tutoring sessions: instructors create and manage activities with defined learning objectives; students interact with a Socratic AI tutor that guides them toward those objectives; the system tracks objective-based scoring per student per activity, with full persistence in Supabase.

---

## Success Criteria

- Instructors can sign in, manage courses and activities, start/end/reset activities, and export student scores as CSV
- Students can sign in, access only ACTIVE activities they are enrolled in, and engage in a Socratic tutoring conversation
- The LLM guides students with questions (never giving direct answers), detects when a learning objective is achieved, and awards +1 score per first achievement
- All interactions are persisted in PostgreSQL via Supabase
- The platform is accessible via a web UI and a FastAPI HTTP API

---

## Out of Scope

- Automatic activity generation from slides
- Student self-enrollment in courses
- Bulk student management
