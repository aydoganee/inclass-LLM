import hashlib
import csv
import io
from app.database import supabase_client


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def _auth_student(email: str, password: str):
    """
    Returns (student_row, None) on success, or (None, error_str) on failure.
    Looks up the student by email and validates the hashed password.
    """
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
    if student.get("password_hash") != _hash(password):
        return None, "Invalid password"
    return student, None


def _auth_instructor(email: str, password: str):
    """
    Returns (instructor_row, None) on success, or (None, error_str) on failure.
    """
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
    if instructor.get("password_hash") != _hash(password):
        return None, "Invalid password"
    return instructor, None


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

def studentLogin(email: str, password: str) -> dict:
    try:
        student, err = _auth_student(email, password)
        if err:
            return {"ok": False, "error": err}
        return {"ok": True, "student": {k: v for k, v in student.items() if k != "password_hash"}}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def setStudentPassword(email: str, password: str) -> dict:
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


def changeStudentPassword(email: str, password: str, new_password: str, old_password: str) -> dict:
    try:
        student, err = _auth_student(email, old_password)
        if err:
            return {"ok": False, "error": err}
        supabase_client.table("students").update({"password_hash": _hash(new_password)}).eq("id", student["id"]).execute()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def getActivity(email: str, password: str, course_id: str, activity_no: int) -> dict:
    try:
        _, err = _auth_student(email, password)
        if err:
            return {"ok": False, "error": err}

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


def logScore(email: str, password: str, course_id: str, activity_no: int, score: float, meta: str | None = None) -> dict:
    try:
        student, err = _auth_student(email, password)
        if err:
            return {"ok": False, "error": err}

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

def instructorLogin(email: str, password: str) -> dict:
    try:
        instructor, err = _auth_instructor(email, password)
        if err:
            return {"ok": False, "error": err}
        return {"ok": True, "instructor": {k: v for k, v in instructor.items() if k != "password_hash"}}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def setInstructorPassword(email: str, password: str | None = None) -> dict:
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


def changeInstructorPassword(email: str, password: str, old_password: str, new_password: str) -> dict:
    try:
        instructor, err = _auth_instructor(email, old_password)
        if err:
            return {"ok": False, "error": err}
        supabase_client.table("instructors").update({"password_hash": _hash(new_password)}).eq("id", instructor["id"]).execute()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def listMyCourses(email: str, password: str) -> dict:
    try:
        instructor, err = _auth_instructor(email, password)
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


def listActivities(email: str, password: str, course_id: str) -> dict:
    try:
        instructor, err = _auth_instructor(email, password)
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
    password: str,
    course_id: str,
    activity_text: str,
    learning_objectives: list[str],
    activity_no_optional: int | None = None,
) -> dict:
    try:
        instructor, err = _auth_instructor(email, password)
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


def updateActivity(email: str, password: str, course_id: str, activity_no: int, patch: dict) -> dict:
    try:
        instructor, err = _auth_instructor(email, password)
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


def startActivity(email: str, password: str, course_id: str, activity_no: int) -> dict:
    try:
        instructor, err = _auth_instructor(email, password)
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


def endActivity(email: str, password: str, course_id: str, activity_no: int) -> dict:
    try:
        instructor, err = _auth_instructor(email, password)
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


def exportScores(email: str, password: str, course_id: str, activity_no: int) -> dict:
    try:
        instructor, err = _auth_instructor(email, password)
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


def resetActivity(email: str, password: str, course_id: str, activity_no: int) -> dict:
    """Delete all score records for this activity and set status to ENDED."""
    try:
        instructor, err = _auth_instructor(email, password)
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


def resetStudentPassword(email: str, password: str, course_id: str, student_email: str, new_password: str) -> dict:
    try:
        instructor, err = _auth_instructor(email, password)
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
