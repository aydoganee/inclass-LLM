import hashlib
import csv
import io
import os
import httpx
from typing import Optional
from app.database import supabase_client



# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def _auth_student(email: str, password: str | None = None, token: str | None = None):
    """
    Returns (student_row, None) on success, or (None, error_str) on failure.
    Looks up the student by email and validates the hashed password or token.
    """
    if not password and not token:
        return None, "No credentials provided"

    try:
        res = (
            supabase_client
            .table("students")
            .select("*")
            .eq("email", email)
            .single()
            .execute()
        )
        student = res.data
    except Exception as e:
        return None, f"Student not found: {e}"
    if student is None:
        return None, "Student not found"

    if token:
        try:
            from google.oauth2 import id_token
            from google.auth.transport import requests as google_requests
            
            client_id = os.environ.get("GOOGLE_CLIENT_ID")
            idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), client_id)
            if idinfo.get("email") != email:
                return None, "Token email mismatch"
            return student, None
        except Exception as e:
            return None, f"Invalid token: {str(e)}"

    if password:
        if student.get("password_hash") != _hash(password):
            return None, "Invalid password"
        return student, None

    return None, "Authentication failed"


def _auth_instructor(email: str, password: str | None = None, token: str | None = None):
    """
    Returns (instructor_row, None) on success, or (None, error_str) on failure.
    """
    if not password and not token:
        return None, "No credentials provided"

    try:
        res = (
            supabase_client
            .table("instructors")
            .select("*")
            .eq("email", email)
            .single()
            .execute()
        )
        instructor = res.data
    except Exception as e:
        return None, f"Instructor not found: {e}"

    if instructor is None:
        return None, "Instructor not found"

    if token:
        try:
            from google.oauth2 import id_token
            from google.auth.transport import requests as google_requests
            
            client_id = os.environ.get("GOOGLE_CLIENT_ID")
            idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), client_id)
            if idinfo.get("email") != email:
                return None, "Token email mismatch"
            return instructor, None
        except Exception as e:
            return None, f"Invalid token: {str(e)}"

    if password:
        if instructor.get("password_hash") != _hash(password):
            return None, "Invalid password"
        return instructor, None

    return None, "Authentication failed"


def _instructor_owns_course(instructor_id, course_id: str) -> bool:
    """Returns True if the instructor owns the given course."""
    try:
        res = (
            supabase_client
            .table("courses")
            .select("id")
            .eq("id", course_id)
            .eq("instructor_id", instructor_id)
            .single()
            .execute()
        )
        return res.data is not None
    except Exception:
        return False


def _student_enrolled_in_course(student_id, course_id: str) -> bool:
    """Returns True if the student is enrolled in the given course."""
    try:
        res = (
            supabase_client
            .table("enrollments")
            .select("id")
            .eq("course_id", course_id)
            .eq("student_id", student_id)
            .single()
            .execute()
        )
        return res.data is not None
    except Exception:
        return False


def _get_activity(course_id: str, activity_no: int):
    """
    Returns (activity_row, None) or (None, error_str).
    """
    try:
        res = (
            supabase_client
            .table("activities")
            .select("*")
            .eq("course_id", course_id)
            .eq("activity_no", activity_no)
            .single()
            .execute()
        )
        if res.data is None:
            return None, "Activity not found"
        return res.data, None
    except Exception as e:
        return None, f"Activity not found: {e}"


# ---------------------------------------------------------------------------
# Student functions
# ---------------------------------------------------------------------------

def studentLogin(email: str, password: str | None = None, token: str | None = None) -> dict:
    try:
        student, err = _auth_student(email, password, token)
        if err:
            return {"ok": False, "error": err}
        return {"ok": True, "student": {k: v for k, v in student.items() if k != "password_hash"}}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def setStudentPassword(email: str, password: str | None = None, token: str | None = None) -> dict:
    """Sets the password only if the student has no password yet."""
    try:
        res = (
            supabase_client
            .table("students")
            .select("id, password_hash")
            .eq("email", email)
            .single()
            .execute()
        )
        student = res.data
    except Exception as e:
        return {"ok": False, "error": f"Student not found: {e}"}

    if student is None:
        return {"ok": False, "error": "Student not found"}
    if student.get("password_hash"):
        return {"ok": False, "error": "Password already set"}

    try:
        supabase_client.table("students").update({"password_hash": _hash(password)}).eq("id", student["id"]).execute()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def changeStudentPassword(email: str, password: str | None = None, new_password: str = "", old_password: str | None = None, token: str | None = None) -> dict:
    try:
        student, err = _auth_student(email, old_password, token)
        if err:
            return {"ok": False, "error": err}
        supabase_client.table("students").update({"password_hash": _hash(new_password)}).eq("id", student["id"]).execute()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def getActivity(email: str, password: str | None = None, course_id: str = "", activity_no: int = 0, token: str | None = None) -> dict:
    try:
        student, err = _auth_student(email, password, token)
        if err:
            return {"ok": False, "error": err}

        if not _student_enrolled_in_course(student["id"], course_id):
            return {"ok": False, "error": "Student is not enrolled in this course"}

        activity, err = _get_activity(course_id, activity_no)
        if err:
            return {"ok": False, "error": err}

        status = activity.get("status")
        if status == "NOT_STARTED":
            return {"ok": False, "error": "Activity has not started yet"}
        if status == "ENDED":
            return {"ok": False, "error": "Activity has ended"}
        if status != "ACTIVE":
            return {"ok": False, "error": f"Unknown activity status: {status}"}

        safe = {k: v for k, v in activity.items() if k != "learning_objectives"}
        return {"ok": True, "activity": safe}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def logScore(email: str, password: str | None = None, course_id: str = "", activity_no: int = 0, score: float = 0.0, meta: str | None = None, token: str | None = None) -> dict:
    try:
        student, err = _auth_student(email, password, token)
        if err:
            return {"ok": False, "error": err}

        if not _student_enrolled_in_course(student["id"], course_id):
            return {"ok": False, "error": "Student is not enrolled in this course"}

        activity, err = _get_activity(course_id, activity_no)
        if err:
            return {"ok": False, "error": err}

        if activity.get("status") != "ACTIVE":
            return {"ok": False, "error": "Activity is not active"}

        record = {
            "student_id": student["id"],
            "activity_id": activity["id"],
            "course_id": course_id,
            "activity_no": activity_no,
            "score": score,
        }
        if meta is not None:
            record["meta"] = meta

        supabase_client.table("scores").insert(record).execute()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ---------------------------------------------------------------------------
# Instructor functions
# ---------------------------------------------------------------------------

def instructorLogin(email: str, password: str | None = None, token: str | None = None) -> dict:
    try:
        instructor, err = _auth_instructor(email, password, token)
        if err:
            return {"ok": False, "error": err}
        return {"ok": True, "instructor": {k: v for k, v in instructor.items() if k != "password_hash"}}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def setInstructorPassword(email: str, password: str | None = None, token: str | None = None) -> dict:
    """Sets the password only if the instructor has no password yet."""
    try:
        res = (
            supabase_client
            .table("instructors")
            .select("id, password_hash")
            .eq("email", email)
            .single()
            .execute()
        )
        instructor = res.data
    except Exception as e:
        return {"ok": False, "error": f"Instructor not found: {e}"}

    if instructor is None:
        return {"ok": False, "error": "Instructor not found"}
    if instructor.get("password_hash"):
        return {"ok": False, "error": "Password already set"}
    if not password:
        return {"ok": False, "error": "Password is required"}

    try:
        supabase_client.table("instructors").update({"password_hash": _hash(password)}).eq("id", instructor["id"]).execute()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def changeInstructorPassword(email: str, password: str | None = None, old_password: str | None = None, new_password: str = "", token: str | None = None) -> dict:
    try:
        instructor, err = _auth_instructor(email, old_password, token)
        if err:
            return {"ok": False, "error": err}
        supabase_client.table("instructors").update({"password_hash": _hash(new_password)}).eq("id", instructor["id"]).execute()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def listMyCourses(email: str, password: str | None = None, token: str | None = None) -> dict:
    try:
        instructor, err = _auth_instructor(email, password, token)
        if err:
            return {"ok": False, "error": err}

        res = (
            supabase_client
            .table("courses")
            .select("*")
            .eq("instructor_id", instructor["id"])
            .execute()
        )
        return {"ok": True, "courses": res.data or []}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def listActivities(email: str, password: str | None = None, course_id: str = "", token: str | None = None) -> dict:
    try:
        instructor, err = _auth_instructor(email, password, token)
        if err:
            return {"ok": False, "error": err}

        if not _instructor_owns_course(instructor["id"], course_id):
            return {"ok": False, "error": "Course not found or access denied"}

        res = (
            supabase_client
            .table("activities")
            .select("*")
            .eq("course_id", course_id)
            .order("activity_no", desc=False)
            .execute()
        )
        return {"ok": True, "activities": res.data or []}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def createActivity(
    email: str,
    password: str | None,
    course_id: str,
    activity_text: str,
    learning_objectives: list[str],
    activity_no_optional: int | None = None,
    token: str | None = None,
) -> dict:
    try:
        instructor, err = _auth_instructor(email, password, token)
        if err:
            return {"ok": False, "error": err}

        if not _instructor_owns_course(instructor["id"], course_id):
            return {"ok": False, "error": "Course not found or access denied"}

        # Determine activity_no
        if activity_no_optional is not None:
            activity_no = activity_no_optional
            # Check for duplicate
            try:
                dup = (
                    supabase_client
                    .table("activities")
                    .select("id")
                    .eq("course_id", course_id)
                    .eq("activity_no", activity_no)
                    .single()
                    .execute()
                )
                if dup.data:
                    return {"ok": False, "error": f"activity_no {activity_no} already exists in this course"}
            except Exception:
                pass  # no duplicate found
        else:
            # Auto-assign: max + 1
            res = (
                supabase_client
                .table("activities")
                .select("activity_no")
                .eq("course_id", course_id)
                .order("activity_no", desc=True)
                .limit(1)
                .execute()
            )
            if res.data:
                activity_no = res.data[0]["activity_no"] + 1
            else:
                activity_no = 1

        record = {
            "course_id": course_id,
            "activity_no": activity_no,
            "activity_text": activity_text,
            "learning_objectives": learning_objectives,
            "status": "NOT_STARTED",
        }
        result = supabase_client.table("activities").insert(record).execute()
        return {"ok": True, "activity": result.data[0] if result.data else record}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def updateActivity(email: str, password: str | None, course_id: str, activity_no: int, patch: dict, token: str | None = None) -> dict:
    try:
        instructor, err = _auth_instructor(email, password, token)
        if err:
            return {"ok": False, "error": err}

        if not _instructor_owns_course(instructor["id"], course_id):
            return {"ok": False, "error": "Course not found or access denied"}

        allowed_fields = {"activity_text", "learning_objectives"}
        filtered = {k: v for k, v in patch.items() if k in allowed_fields}
        if not filtered:
            return {"ok": False, "error": "No updatable fields provided (allowed: activity_text, learning_objectives)"}

        activity, err = _get_activity(course_id, activity_no)
        if err:
            return {"ok": False, "error": err}

        result = (
            supabase_client
            .table("activities")
            .update(filtered)
            .eq("id", activity["id"])
            .execute()
        )
        return {"ok": True, "activity": result.data[0] if result.data else None}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def startActivity(email: str, password: str | None, course_id: str, activity_no: int, token: str | None = None) -> dict:
    try:
        instructor, err = _auth_instructor(email, password, token)
        if err:
            return {"ok": False, "error": err}

        if not _instructor_owns_course(instructor["id"], course_id):
            return {"ok": False, "error": "Course not found or access denied"}

        activity, err = _get_activity(course_id, activity_no)
        if err:
            return {"ok": False, "error": err}

        supabase_client.table("activities").update({"status": "ACTIVE"}).eq("id", activity["id"]).execute()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def endActivity(email: str, password: str | None, course_id: str, activity_no: int, token: str | None = None) -> dict:
    try:
        instructor, err = _auth_instructor(email, password, token)
        if err:
            return {"ok": False, "error": err}

        if not _instructor_owns_course(instructor["id"], course_id):
            return {"ok": False, "error": "Course not found or access denied"}

        activity, err = _get_activity(course_id, activity_no)
        if err:
            return {"ok": False, "error": err}

        supabase_client.table("activities").update({"status": "ENDED"}).eq("id", activity["id"]).execute()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def exportScores(email: str, password: str | None, course_id: str, activity_no: int, token: str | None = None) -> dict:
    try:
        instructor, err = _auth_instructor(email, password, token)
        if err:
            return {"ok": False, "error": err}

        if not _instructor_owns_course(instructor["id"], course_id):
            return {"ok": False, "error": "Course not found or access denied"}

        activity, err = _get_activity(course_id, activity_no)
        if err:
            return {"ok": False, "error": err}

        res = (
            supabase_client
            .table("scores")
            .select("*, students(email)")
            .eq("activity_id", activity["id"])
            .execute()
        )
        rows = res.data or []

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["student_email", "score", "meta", "created_at"])
        for row in rows:
            student_email = (row.get("students") or {}).get("email", "")
            writer.writerow([student_email, row.get("score", ""), row.get("meta", ""), row.get("created_at", "")])

        return {"ok": True, "csv": output.getvalue()}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def resetActivity(email: str, password: str | None, course_id: str, activity_no: int, token: str | None = None) -> dict:
    """Delete all score records for this activity and set status to ENDED."""
    try:
        instructor, err = _auth_instructor(email, password, token)
        if err:
            return {"ok": False, "error": err}

        if not _instructor_owns_course(instructor["id"], course_id):
            return {"ok": False, "error": "Course not found or access denied"}

        activity, err = _get_activity(course_id, activity_no)
        if err:
            return {"ok": False, "error": err}

        # Delete all scores
        supabase_client.table("scores").delete().eq("activity_id", activity["id"]).execute()
        # Set status to ENDED
        supabase_client.table("activities").update({"status": "ENDED"}).eq("id", activity["id"]).execute()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def chat(email: str, password: str | None = None, course_id: str = "", activity_no: int = 0, message: str = "", token: str | None = None) -> dict:
    """US-J: Student tutoring flow via LLM."""
    try:
        # Authenticate
        student, err = _auth_student(email, password, token)
        if err:
            return {"ok": False, "error": err}

        # Check activity is ACTIVE
        activity, err = _get_activity(course_id, activity_no)
        if err:
            return {"ok": False, "error": err}
        if activity.get("status") != "ACTIVE":
            return {"ok": False, "error": "Activity is not active"}

        # Check enrollment
        if not _student_enrolled_in_course(student["id"], course_id):
            return {"ok": False, "error": "Student is not enrolled in this course"}

        # Load or create student_progress
        try:
            progress_res = (
                supabase_client
                .table("student_progress")
                .select("*")
                .eq("student_id", student["id"])
                .eq("course_id", course_id)
                .eq("activity_no", activity_no)
                .single()
                .execute()
            )
            progress = progress_res.data
        except Exception:
            progress = None

        if progress is None:
            new_progress = {
                "student_id": student["id"],
                "course_id": course_id,
                "activity_no": activity_no,
                "conversation_history": [],
                "achieved_objectives": [],
                "is_completed": False,
            }
            insert_res = supabase_client.table("student_progress").insert(new_progress).execute()
            progress = insert_res.data[0] if insert_res.data else new_progress

        if progress.get("is_completed"):
            return {"ok": False, "error": "Activity already completed"}

        conversation_history = progress.get("conversation_history") or []
        achieved_objectives = progress.get("achieved_objectives") or []
        learning_objectives = activity.get("learning_objectives") or []

        # Build system prompt
        objectives_str = "\n".join(f"- {obj}" for obj in learning_objectives)
        system_prompt = f"""You are an expert Socratic tutor integrated into a university classroom activity system. Your role is to guide students toward genuine understanding through thoughtful questioning — never by giving away answers.

## Context
Activity: {activity["activity_text"]}

Learning Objectives (CONFIDENTIAL — never mention or list these to the student):
{objectives_str}

## Your Behavior Rules

### Questioning
- Ask exactly ONE clear, focused question per response.
- Start from the student's current level — if their answer is vague, ask a simpler clarifying question first.
- Gradually increase depth: start with "what", move to "how", then "why".
- Never ask multiple questions in one turn.

### Guidance Style
- Use the Socratic method: respond to the student's answer, acknowledge what is correct, gently challenge what is incomplete.
- Never reveal learning objectives directly.
- Never give the full answer — guide the student to discover it themselves.
- If the student is stuck, provide a small conceptual hint, then ask again.
- Always use correct academic terminology from the activity.
- All responses must be in English.

### Objective Detection
- Carefully evaluate each student response against the learning objectives.
- An objective is achieved when the student's own words clearly demonstrate understanding of that concept — not just when they repeat a keyword.
- When an objective is achieved, append this exact JSON marker on a new line at the end of your response (replace with exact objective text):
  {{"objective_achieved": "EXACT_OBJECTIVE_TEXT"}}
- Only mark an objective as achieved once. Do not re-award it.
- After marking an objective, continue naturally with the next guiding question toward the remaining objectives.

### Completion
- When ALL objectives have been achieved, write a brief congratulatory message summarizing what the student learned, then append on a new line:
  {{"all_objectives_completed": true}}

### Tone
- Be encouraging and patient.
- Celebrate correct answers briefly before moving on.
- Never be condescending or dismissive.
- Keep responses concise — 2 to 4 sentences maximum before the question.

## Important
You are an academic tool used in a real university course. Accuracy, clarity, and pedagogical quality matter. Never go off-topic. Never discuss anything outside the scope of the activity."""

        # Build messages list
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": message})

        # Call OpenRouter
        api_key = os.environ["OPENROUTER_API_KEY"]
        with httpx.Client(timeout=60) as client:
            resp = client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "inclusionai/ling-2.6-flash:free",
                    "messages": messages,
                },
            )
            resp.raise_for_status()
            llm_response_text = resp.json()["choices"][0]["message"]["content"]

        # Parse objective_achieved markers
        newly_achieved = []
        import re
        for match in re.finditer(r'\{"objective_achieved":\s*"([^"]+)"\}', llm_response_text):
            objective = match.group(1)
            if objective not in achieved_objectives:
                achieved_objectives.append(objective)
                newly_achieved.append(objective)

        # Log score for each newly achieved objective
        for objective in newly_achieved:
            logScore(email, password, course_id, activity_no, score=1.0, meta=f"Objective achieved: {objective}")

        # Check completion
        is_completed = bool(re.search(r'\{"all_objectives_completed":\s*true\}', llm_response_text))

        # Update conversation history
        conversation_history.append({"role": "user", "content": message})
        conversation_history.append({"role": "assistant", "content": llm_response_text})

        # Save progress
        supabase_client.table("student_progress").update({
            "conversation_history": conversation_history,
            "achieved_objectives": achieved_objectives,
            "is_completed": is_completed,
            "updated_at": "now()",
        }).eq("student_id", student["id"]).eq("course_id", course_id).eq("activity_no", activity_no).execute()

        return {
            "ok": True,
            "response": llm_response_text,
            "score": len(achieved_objectives),
            "completed": is_completed,
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


def resetStudentPassword(email: str, password: str | None, course_id: str, student_email: str, new_password: str, token: str | None = None) -> dict:
    try:
        instructor, err = _auth_instructor(email, password, token)
        if err:
            return {"ok": False, "error": err}

        if not _instructor_owns_course(instructor["id"], course_id):
            return {"ok": False, "error": "Course not found or access denied"}

        # Verify the student belongs to this course
        try:
            enrollment = (
                supabase_client
                .table("enrollments")
                .select("student_id, students(id, email)")
                .eq("course_id", course_id)
                .execute()
            )
            student_id = None
            for row in (enrollment.data or []):
                s = row.get("students") or {}
                if s.get("email") == student_email:
                    student_id = s.get("id")
                    break
        except Exception as e:
            return {"ok": False, "error": f"Failed to look up student: {e}"}

        if student_id is None:
            return {"ok": False, "error": "Student not found in this course"}

        supabase_client.table("students").update({"password_hash": _hash(new_password)}).eq("id", student_id).execute()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}
def logManualScore(
    email: str,
    password: str | None,
    course_id: str,
    activity_no: int,
    student_email: str,
    score: float,
    token: str | None = None,
) -> dict:
    try:
        instructor, err = _auth_instructor(email, password, token)
        if err:
            return {"ok": False, "error": err}

        if not _instructor_owns_course(instructor["id"], course_id):
            return {"ok": False, "error": "Course not found or access denied"}

        activity, err = _get_activity(course_id, activity_no)
        if err:
            return {"ok": False, "error": err}

        student_res = (
            supabase_client
            .table("students")
            .select("id, email")
            .eq("email", student_email)
            .single()
            .execute()
        )
        student = student_res.data

        if student is None:
            return {"ok": False, "error": "Student not found"}

        if not _student_enrolled_in_course(student["id"], course_id):
            return {"ok": False, "error": "Student is not enrolled in this course"}

        record = {
            "student_id": student["id"],
            "activity_id": activity["id"],
            "course_id": course_id,
            "activity_no": activity_no,
            "score": score,
            "meta": "Manual grading event",
        }

        result = supabase_client.table("scores").insert(record).execute()

        return {
            "ok": True,
            "score": result.data[0] if result.data else record
        }

    except Exception as e:
        return {"ok": False, "error": str(e)}