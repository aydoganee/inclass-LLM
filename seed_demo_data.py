"""
US-T6: Demo Preparation — Seed Supabase with demo data
Owner: Oğuzhan Elmas

Usage:
    python seed_demo_data.py

Requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in environment
(or in a .env file loaded before running).

Demo credentials after seeding
-------------------------------
Instructor : demo_instructor@mef.edu.tr  / DemoPass123
Students   : alice@student.mef.edu.tr    / StudentPass1
             bob@student.mef.edu.tr      / StudentPass2
             carol@student.mef.edu.tr    / StudentPass3
Course ID  : COMP101-DEMO
"""

import hashlib
import os
import sys

# Allow running without activating the venv manually.
try:
    from supabase import create_client
except ImportError:
    print("ERROR: supabase-py not installed. Run: pip install supabase")
    sys.exit(1)


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def seed():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        print("ERROR: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set.")
        sys.exit(1)

    db = create_client(url, key)

    # ------------------------------------------------------------------
    # 1. Instructor
    # ------------------------------------------------------------------
    instructor_email = "demo_instructor@mef.edu.tr"
    instructor_pass = "DemoPass123"

    existing = db.table("instructors").select("id").eq("email", instructor_email).execute()
    if existing.data:
        instructor_id = existing.data[0]["id"]
        db.table("instructors").update({"password_hash": _hash(instructor_pass)}).eq("id", instructor_id).execute()
        print(f"[instructor] updated: {instructor_email}")
    else:
        res = db.table("instructors").insert({
            "email": instructor_email,
            "password_hash": _hash(instructor_pass),
        }).execute()
        instructor_id = res.data[0]["id"]
        print(f"[instructor] created: {instructor_email}")

    # ------------------------------------------------------------------
    # 2. Course
    # ------------------------------------------------------------------
    course_id = "COMP101-DEMO"

    existing = db.table("courses").select("id").eq("id", course_id).execute()
    if not existing.data:
        db.table("courses").insert({
            "id": course_id,
            "name": "Introduction to Computer Networks (Demo)",
            "instructor_id": instructor_id,
        }).execute()
        print(f"[course] created: {course_id}")
    else:
        db.table("courses").update({"instructor_id": instructor_id}).eq("id", course_id).execute()
        print(f"[course] updated: {course_id}")

    # ------------------------------------------------------------------
    # 3. Students
    # ------------------------------------------------------------------
    students_config = [
        {"email": "alice@student.mef.edu.tr", "password": "StudentPass1"},
        {"email": "bob@student.mef.edu.tr",   "password": "StudentPass2"},
        {"email": "carol@student.mef.edu.tr", "password": "StudentPass3"},
    ]
    student_ids = []
    for s in students_config:
        existing = db.table("students").select("id").eq("email", s["email"]).execute()
        if existing.data:
            sid = existing.data[0]["id"]
            db.table("students").update({"password_hash": _hash(s["password"])}).eq("id", sid).execute()
            print(f"[student] updated: {s['email']}")
        else:
            res = db.table("students").insert({
                "email": s["email"],
                "password_hash": _hash(s["password"]),
            }).execute()
            sid = res.data[0]["id"]
            print(f"[student] created: {s['email']}")
        student_ids.append(sid)

    # ------------------------------------------------------------------
    # 4. Enrollments
    # ------------------------------------------------------------------
    for sid in student_ids:
        existing = (
            db.table("enrollments")
            .select("id")
            .eq("course_id", course_id)
            .eq("student_id", sid)
            .execute()
        )
        if not existing.data:
            db.table("enrollments").insert({"course_id": course_id, "student_id": sid}).execute()
            print(f"[enrollment] created student {sid} → {course_id}")

    # ------------------------------------------------------------------
    # 5. Activities
    # ------------------------------------------------------------------
    activities_config = [
        {
            "activity_no": 1,
            "activity_text": (
                "The OSI (Open Systems Interconnection) model is a conceptual framework "
                "that standardizes the functions of a telecommunication or computing system "
                "into seven abstraction layers: Physical, Data Link, Network, Transport, "
                "Session, Presentation, and Application."
            ),
            "learning_objectives": [
                "List all seven OSI layers in correct order",
                "Describe the role of the Network layer",
                "Explain the difference between TCP and UDP at the Transport layer",
            ],
            "status": "ACTIVE",
        },
        {
            "activity_no": 2,
            "activity_text": (
                "TCP/IP is the foundational suite of protocols for the Internet. "
                "It maps to a simplified four-layer model: Link, Internet, Transport, and Application. "
                "The IP protocol handles addressing and routing; TCP provides reliable, ordered delivery."
            ),
            "learning_objectives": [
                "Explain the purpose of IP addresses",
                "Describe the TCP three-way handshake",
                "Distinguish between IPv4 and IPv6",
            ],
            "status": "ENDED",
        },
    ]

    activity_ids = {}
    for act in activities_config:
        existing = (
            db.table("activities")
            .select("id")
            .eq("course_id", course_id)
            .eq("activity_no", act["activity_no"])
            .execute()
        )
        record = {
            "course_id": course_id,
            "activity_no": act["activity_no"],
            "activity_text": act["activity_text"],
            "learning_objectives": act["learning_objectives"],
            "status": act["status"],
        }
        if existing.data:
            aid = existing.data[0]["id"]
            db.table("activities").update(record).eq("id", aid).execute()
            print(f"[activity] updated: activity_no={act['activity_no']} ({act['status']})")
        else:
            res = db.table("activities").insert(record).execute()
            aid = res.data[0]["id"]
            print(f"[activity] created: activity_no={act['activity_no']} ({act['status']})")
        activity_ids[act["activity_no"]] = aid

    # ------------------------------------------------------------------
    # 6. Demo scores (for activity 1 — ACTIVE, so export can be shown)
    # ------------------------------------------------------------------
    scores_config = [
        # (student_index, score, meta)
        (0, 1.0, "Objective achieved: List all seven OSI layers in correct order"),
        (1, 1.0, "Objective achieved: List all seven OSI layers in correct order"),
        (1, 1.0, "Objective achieved: Describe the role of the Network layer"),
        (2, 1.0, "Objective achieved: List all seven OSI layers in correct order"),
        (2, 1.0, "Objective achieved: Describe the role of the Network layer"),
        (2, 1.0, "Objective achieved: Explain the difference between TCP and UDP at the Transport layer"),
    ]

    act1_id = activity_ids[1]
    existing_scores = db.table("scores").select("id").eq("activity_id", act1_id).execute()
    if not existing_scores.data:
        for student_idx, score_val, meta_val in scores_config:
            db.table("scores").insert({
                "student_id": student_ids[student_idx],
                "activity_id": act1_id,
                "course_id": course_id,
                "activity_no": 1,
                "score": score_val,
                "meta": meta_val,
            }).execute()
        print(f"[scores] inserted {len(scores_config)} demo score records for activity 1")
    else:
        print(f"[scores] skipped (already exist for activity 1)")

    print()
    print("=" * 60)
    print("Demo seed complete.")
    print("=" * 60)
    print(f"  Instructor : {instructor_email}  /  {instructor_pass}")
    for s in students_config:
        print(f"  Student    : {s['email']}  /  {s['password']}")
    print(f"  Course ID  : {course_id}")
    print(f"  Activities : 1 (ACTIVE), 2 (ENDED)")
    print("=" * 60)


if __name__ == "__main__":
    # Load .env if python-dotenv is available
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    seed()
