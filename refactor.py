import re

with open('app/services.py', 'r') as f:
    content = f.read()

# Replace _auth_instructor signature and implementation
old_auth = '''def _auth_instructor(email: str, password: str):
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
    return instructor, None'''

new_auth = '''def _auth_instructor(email: str, password: str | None = None, token: str | None = None):
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

    return None, "Authentication failed"'''

content = content.replace(old_auth, new_auth)

# Now for each instructor function, we need to update its signature to accept token
# instructorLogin
content = content.replace('def instructorLogin(email: str, password: str) -> dict:', 'def instructorLogin(email: str, password: str | None = None, token: str | None = None) -> dict:')
content = content.replace('instructor, err = _auth_instructor(email, password)', 'instructor, err = _auth_instructor(email, password, token)')

# setInstructorPassword
content = content.replace('def setInstructorPassword(email: str, password: str | None = None) -> dict:', 'def setInstructorPassword(email: str, password: str | None = None, token: str | None = None) -> dict:')

# changeInstructorPassword
content = content.replace('def changeInstructorPassword(email: str, password: str, old_password: str, new_password: str) -> dict:', 'def changeInstructorPassword(email: str, password: str | None = None, old_password: str | None = None, new_password: str = "", token: str | None = None) -> dict:')
content = content.replace('instructor, err = _auth_instructor(email, old_password)', 'instructor, err = _auth_instructor(email, old_password, token)')

# listMyCourses
content = content.replace('def listMyCourses(email: str, password: str) -> dict:', 'def listMyCourses(email: str, password: str | None = None, token: str | None = None) -> dict:')

# listActivities
content = content.replace('def listActivities(email: str, password: str, course_id: str) -> dict:', 'def listActivities(email: str, password: str | None = None, course_id: str = "", token: str | None = None) -> dict:')

# createActivity
content = content.replace('def createActivity(\n    email: str,\n    password: str,\n    course_id: str,\n    activity_text: str,\n    learning_objectives: list[str],\n    activity_no_optional: int | None = None,\n) -> dict:', 'def createActivity(\n    email: str,\n    password: str | None,\n    course_id: str,\n    activity_text: str,\n    learning_objectives: list[str],\n    activity_no_optional: int | None = None,\n    token: str | None = None,\n) -> dict:')

# updateActivity
content = content.replace('def updateActivity(email: str, password: str, course_id: str, activity_no: int, patch: dict) -> dict:', 'def updateActivity(email: str, password: str | None, course_id: str, activity_no: int, patch: dict, token: str | None = None) -> dict:')

# startActivity
content = content.replace('def startActivity(email: str, password: str, course_id: str, activity_no: int) -> dict:', 'def startActivity(email: str, password: str | None, course_id: str, activity_no: int, token: str | None = None) -> dict:')

# endActivity
content = content.replace('def endActivity(email: str, password: str, course_id: str, activity_no: int) -> dict:', 'def endActivity(email: str, password: str | None, course_id: str, activity_no: int, token: str | None = None) -> dict:')

# exportScores
content = content.replace('def exportScores(email: str, password: str, course_id: str, activity_no: int) -> dict:', 'def exportScores(email: str, password: str | None, course_id: str, activity_no: int, token: str | None = None) -> dict:')

# resetActivity
content = content.replace('def resetActivity(email: str, password: str, course_id: str, activity_no: int) -> dict:', 'def resetActivity(email: str, password: str | None, course_id: str, activity_no: int, token: str | None = None) -> dict:')

# resetStudentPassword
content = content.replace('def resetStudentPassword(email: str, password: str, course_id: str, student_email: str, new_password: str) -> dict:', 'def resetStudentPassword(email: str, password: str | None, course_id: str, student_email: str, new_password: str, token: str | None = None) -> dict:')

with open('app/services.py', 'w') as f:
    f.write(content)

print("Refactoring complete.")
