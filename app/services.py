from __future__ import annotations

import hashlib
import csv
import io
import json
import logging
import os
import re
import traceback
import httpx
from typing import Optional
from app.database import supabase_client


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def _auth_student(email: str, password: str | None = None):
    """
    Returns (student_row, None) on success, or (None, error_str) on failure.
    If the student has no password_hash (Google-only account), password check is skipped.
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

    if student.get("password_hash") is None:
        return student, None

    if not password:
        return None, "No credentials provided"

    if student.get("password_hash") != _hash(password):
        return None, "Invalid password"
    return student, None


def _auth_instructor(email: str, password: str | None = None):
    """
    Returns (instructor_row, None) on success, or (None, error_str) on failure.
    If the instructor has no password_hash (Google-only account), password check is skipped.
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

    if instructor.get("password_hash") is None:
        return instructor, None

    if not password:
        return None, "No credentials provided"

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


def _extract_google_email(token: str):
    """
    Verifies the Google ID token and returns (email, None) on success
    or (None, error_str) on failure.
    """
    try:
        from google.oauth2 import id_token
        from google.auth.transport import requests as google_requests
        client_id = os.environ.get("GOOGLE_CLIENT_ID")
        print(f"[Google] Verifying token, GOOGLE_CLIENT_ID set: {bool(client_id)}")
        idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), client_id)
        email = idinfo.get("email")
        if not email:
            return None, "No email in token"
        print(f"Google email: {email}")
        return email, None
    except Exception as e:
        print(f"[Google] Token verification error: {e}")
        traceback.print_exc()
        return None, f"Invalid token: {str(e)}"


# ---------------------------------------------------------------------------
# Student functions
# ---------------------------------------------------------------------------

def studentLogin(email: str, password: str, token: str | None = None) -> dict:
    try:
        if token:
            try:
                google_email, err = _extract_google_email(token)
                if err:
                    print(f"Google auth error: {err}")
                    return {"ok": False, "error": err}
                print(f"[studentLogin] Looking up student with email: {google_email}")
                res = supabase_client.table("students").select("*").eq("email", google_email).single().execute()
                student = res.data
                print(f"[studentLogin] Supabase result: {student}")
                if student is None:
                    return {"ok": False, "error": "Student not found"}
            except Exception as e:
                print(f"Google auth error: {e}")
                traceback.print_exc()
                return {"ok": False, "error": str(e)}
        else:
            student, err = _auth_student(email, password)
            if err:
                return {"ok": False, "error": err}
        student_data = {k: v for k, v in student.items() if k != "password_hash"}
        print(f"[studentLogin] Login successful for: {student_data.get('email')}")
        return {"ok": True, "email": student_data.get("email"), "student": student_data}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def setStudentPassword(email: str, password: str) -> dict:
    """Sets the password only if the student has no password yet."""
    if not password:
        return {"ok": False, "error": "Password is required"}

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
        student, err = _auth_student(email, password)
        if err:
            return {"ok": False, "error": err}
        if student.get("password_hash") != _hash(old_password):
            return {"ok": False, "error": "Old password does not match"}
        supabase_client.table("students").update({"password_hash": _hash(new_password)}).eq("id", student["id"]).execute()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def getActivity(email: str, password: str, course_id: str = "", activity_no: int = 0) -> dict:
    try:
        student, err = _auth_student(email, password)
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


def logScore(email: str, password: str, course_id: str = "", activity_no: int = 0, score: float = 0.0, meta: str | None = None) -> dict:
    try:
        student, err = _auth_student(email, password)
        if err:
            return {"ok": False, "error": err}

        if not _student_enrolled_in_course(student["id"], course_id):
            return {"ok": False, "error": "Student is not enrolled in this course"}

        activity, err = _get_activity(course_id, activity_no)
        if err:
            return {"ok": False, "error": err}

        if activity.get("status") != "ACTIVE":
            return {"ok": False, "error": "Activity is not active"}

        # TEKRAR KONTROLÜ (US-K Kuralı: Repeated achievement does not add score again)
        # Sadece meta parametresi doluysa (yani spesifik bir objective başıldıysa) kontrol et
        if meta:
            existing_score_res = (
                supabase_client
                .table("scores")
                .select("id")
                .eq("student_id", student["id"])
                .eq("course_id", course_id)
                .eq("activity_no", activity_no)
                .eq("meta", meta)
                .execute()
            )
            if existing_score_res.data:
                return {"ok": True, "message": "Objective already achieved, score not duplicated"}

        import datetime
        record = {
            "student_id": student["id"],
            "course_id": course_id,
            "activity_no": activity_no,
            "score": score,
            "logged_at": datetime.datetime.now(datetime.UTC).isoformat(),
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

def instructorLogin(email: str, password: str, token: str | None = None) -> dict:
    try:
        if token:
            google_email, err = _extract_google_email(token)
            if err:
                return {"ok": False, "error": err}
            try:
                res = supabase_client.table("instructors").select("*").eq("email", google_email).single().execute()
                instructor = res.data
            except Exception as e:
                return {"ok": False, "error": f"Instructor not found: {e}"}
            if instructor is None:
                return {"ok": False, "error": "Instructor not found"}
        else:
            instructor, err = _auth_instructor(email, password)
            if err:
                return {"ok": False, "error": err}
        instructor_data = {k: v for k, v in instructor.items() if k != "password_hash"}
        print(f"[instructorLogin] Login successful for: {instructor_data.get('email')}")
        return {"ok": True, "email": instructor_data.get("email"), "instructor": instructor_data}
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
        instructor, err = _auth_instructor(email, password)
        if err:
            return {"ok": False, "error": err}
        if instructor.get("password_hash") != _hash(old_password):
            return {"ok": False, "error": "Old password does not match"}
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
            .select("id, name")
            .eq("instructor_id", instructor["id"])
            .execute()
        )

        return {"ok": True, "courses": res.data or []}

    except Exception as e:
        return {"ok": False, "error": str(e)}
    

def listActivities(email: str, password: str, course_id: str = "") -> dict:
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
            .eq("course_id", course_id)
            .eq("activity_no", activity_no)
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
        supabase_client.table("scores").delete().eq("course_id", course_id).eq("activity_no", activity_no).execute()

        # Ekstra: Öğrenci ilerlemelerini de sil (Altay'ın oluşturduğu tablo)
        try:
            supabase_client.table("student_progress").delete().eq("course_id", course_id).eq("activity_no",
                                                                                             activity_no).execute()
        except Exception as e:
            pass  # Tablo yoksa veya hata verirse ana akışı bozmasın

        # Set status to ENDED
        supabase_client.table("activities").update({"status": "ENDED"}).eq("id", activity["id"]).execute()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def chat(email: str, password: str, course_id: str = "", activity_no: int = 0, message: str = "") -> dict:
    """US-J: Student tutoring flow via LLM."""
    try:
        # Authenticate
        student, err = _auth_student(email, password)
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
        system_prompt = f"""You are a warm university instructor. Your role is to teach for conceptual mastery using Socratic questions and academic explanations.

## Activity
{activity["activity_text"]}

## Learning Objectives (CONFIDENTIAL - never mention, list, or reveal these to the student)
{objectives_str}

## Already Achieved Objectives (do not re-award these)
{json.dumps(progress["achieved_objectives"])}

## Rules

⚠️ MANDATORY OUTPUT FORMAT RULE ⚠️
When a student demonstrates understanding of an objective, your response MUST end with this exact JSON on a new line — NO EXCEPTIONS:
{{"objective_achieved": "EXACT_OBJECTIVE_TEXT"}}

If you do not include this marker, the scoring system will fail and the student will not receive their point. This is a system requirement, not optional.

Example — if student understood "3-way handshake":
[your response text here]
{{"objective_achieved": "3-way handshake"}}

Do NOT forget this marker. Do NOT skip it. It must be the last line of your response when an objective is achieved.

### Questioning
- Ask exactly ONE question per response.
- Never directly teach or explain anything before a score is earned.
- Guide the student toward objectives using Socratic questioning.
- All responses must be in English using activity terminology.
- Never use the words "objective" or "learning objective".
- Never reveal the objectives list to the student.

### When a student demonstrates understanding of an objective
When the student's response clearly demonstrates understanding of one of the learning objectives (that is NOT already in achieved objectives):
1. Briefly acknowledge their correct answer.
2. Announce their updated score: "Your current score is X." (calculate X as len(achieved_objectives) + 1)
3. Give a short academic mini-lesson (3-5 sentences) about that concept with a bold heading.
4. Ask the next guiding question toward remaining objectives.
5. At the end of your response, on a new line, append this exact JSON marker:
   {{"objective_achieved": "EXACT_OBJECTIVE_TEXT"}}
   Replace EXACT_OBJECTIVE_TEXT with the exact text from the objectives list above.

### Completion
When ALL objectives have been achieved (nothing left in objectives list):
1. Congratulate the student warmly.
2. Summarize everything they learned in 2-3 sentences.
3. On a new line append: {{"all_objectives_completed": true}}

### First Message Rule
When this is the first message (conversation history is empty or only has the student's first message):
- Start your response by presenting the activity scenario to the student.
- Say something like: "Here's today's activity:" and then show the activity_text exactly.
- Then ask your first guiding question.
- Do NOT skip showing the activity text on the first response.

### Hard rules
- Never re-award an already achieved objective.
- Never reveal achieved or remaining objective texts to the student.
- Keep responses concise and academic (max 4-5 sentences before the question).
- Never go off-topic from the activity."""

        # Build messages list
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": message})

        # Call OpenAI
        api_key = os.environ["OPENAI_API_KEY"]
        with httpx.Client(timeout=60) as client:
            resp = client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": messages,
                    "temperature": 0.3,
                    "top_p": 0.9,
                },
            )
            resp.raise_for_status()
            llm_response_text = resp.json()["choices"][0]["message"]["content"]

        # Parse objective_achieved markers
        logging.warning(f"RAW LLM RESPONSE: {llm_response_text}")
        newly_achieved = []
        for match in re.finditer(r'\{"objective_achieved":\s*"([^"]+)"\}', llm_response_text):
            objective = match.group(1)
            if objective not in achieved_objectives:
                achieved_objectives.append(objective)
                newly_achieved.append(objective)
        print(f"[chat] newly_achieved from regex: {newly_achieved}")

        # Semantic fallback: if no marker found, ask LLM to evaluate student message
        if not newly_achieved:
            remaining_objectives = [o for o in learning_objectives if o not in achieved_objectives]
            if remaining_objectives:
                semantic_prompt = f"""You are evaluating whether a student demonstrated understanding of learning objectives.

Student's message: "{message}"

Learning objectives to check:
{json.dumps(remaining_objectives)}

Instructions:
- Be GENEROUS in your evaluation
- If the student's answer shows even partial understanding of the core concept, mark it as achieved
- Do not require exact wording - synonyms and paraphrases count
- Key concepts to look for:
  * "active recall/retrieval", "memory", "explaining from memory" → first objective
  * "feedback", "checking mistakes", "correcting errors", "misconceptions" → second objective
- Return ONLY a JSON array of achieved objective texts
- Return [] if the student's answer is completely off-topic or irrelevant

Example output: ["Explain that active retrieval practice improves long-term learning more than passive rereading."]
"""
                try:
                    with httpx.Client(timeout=30) as client:
                        semantic_resp = client.post(
                            "https://api.openai.com/v1/chat/completions",
                            headers={
                                "Authorization": f"Bearer {api_key}",
                                "Content-Type": "application/json",
                            },
                            json={
                                "model": "gpt-4o-mini",
                                "messages": [{"role": "user", "content": semantic_prompt}],
                                "max_tokens": 100,
                            },
                        )
                        semantic_resp.raise_for_status()
                        semantic_text = semantic_resp.json()["choices"][0]["message"]["content"].strip()
                        semantic_achieved = json.loads(semantic_text)
                        if isinstance(semantic_achieved, list):
                            for objective in semantic_achieved:
                                if objective in remaining_objectives and objective not in achieved_objectives:
                                    achieved_objectives.append(objective)
                                    newly_achieved.append(objective)
                except Exception as e:
                    logging.warning(f"Semantic check failed: {e}")

        print(f"[chat] newly_achieved after semantic fallback: {newly_achieved}")
        # Log score for each newly achieved objective
        for objective in newly_achieved:
            print(f"[chat] Calling logScore for objective: {objective}")
            result = logScore(email, password, course_id, activity_no, score=1.0, meta=f"Objective achieved: {objective}")
            print(f"[chat] logScore result: {result}")

        # Check completion and auto-complete any skipped objectives
        is_completed = bool(re.search(r'\{"all_objectives_completed":\s*true\}', llm_response_text))
        if is_completed:
            remaining = [o for o in learning_objectives if o not in achieved_objectives]
            for obj in remaining:
                print(f"[chat] Auto-completing remaining objective: {obj}")
                result = logScore(email, password, course_id, activity_no, score=1.0, meta=f"Auto-completed: {obj}")
                print(f"[chat] Auto-complete logScore result: {result}")
                achieved_objectives.append(obj)

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


def gradeStudent(email: str, password: str, course_id: str, activity_no: int, student_email: str, score: float, meta: str | None = None) -> dict:
    """Instructor manually grades a student for an activity."""
    try:
        instructor, err = _auth_instructor(email, password)
        if err:
            return {"ok": False, "error": err}

        if not _instructor_owns_course(instructor["id"], course_id):
            return {"ok": False, "error": "Course not found or access denied"}

        try:
            student_res = supabase_client.table("students").select("id").eq("email", student_email).single().execute()
            student = student_res.data
        except Exception as e:
            return {"ok": False, "error": f"Student not found: {e}"}

        if student is None:
            return {"ok": False, "error": "Student not found"}

        import datetime
        record = {
            "student_id": student["id"],
            "course_id": course_id,
            "activity_no": activity_no,
            "score": score,
            "logged_at": datetime.datetime.utcnow().isoformat(),
        }
        if meta is not None:
            record["meta"] = meta

        supabase_client.table("scores").insert(record).execute()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}
