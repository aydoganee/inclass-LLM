import re

with open('app/services.py', 'r') as f:
    content = f.read()

# Replace _auth_student signature and implementation
old_auth = '''def _auth_student(email: str, password: str):
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
    return student, None'''

new_auth = '''def _auth_student(email: str, password: str | None = None, token: str | None = None):
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

    return None, "Authentication failed"'''

content = content.replace(old_auth, new_auth)

# Now for each student function, we need to update its signature to accept token
# studentLogin
content = content.replace('def studentLogin(email: str, password: str) -> dict:', 'def studentLogin(email: str, password: str | None = None, token: str | None = None) -> dict:')
content = content.replace('student, err = _auth_student(email, password)', 'student, err = _auth_student(email, password, token)')

# setStudentPassword
content = content.replace('def setStudentPassword(email: str, password: str) -> dict:', 'def setStudentPassword(email: str, password: str | None = None, token: str | None = None) -> dict:')

# changeStudentPassword
content = content.replace('def changeStudentPassword(email: str, password: str, new_password: str, old_password: str) -> dict:', 'def changeStudentPassword(email: str, password: str | None = None, new_password: str = "", old_password: str | None = None, token: str | None = None) -> dict:')
content = content.replace('student, err = _auth_student(email, old_password)', 'student, err = _auth_student(email, old_password, token)')

# getActivity
content = content.replace('def getActivity(email: str, password: str, course_id: str, activity_no: int) -> dict:', 'def getActivity(email: str, password: str | None = None, course_id: str = "", activity_no: int = 0, token: str | None = None) -> dict:')
content = content.replace('_, err = _auth_student(email, password)', '_, err = _auth_student(email, password, token)')

# logScore
content = content.replace('def logScore(email: str, password: str, course_id: str, activity_no: int, score: float, meta: str | None = None) -> dict:', 'def logScore(email: str, password: str | None = None, course_id: str = "", activity_no: int = 0, score: float = 0.0, meta: str | None = None, token: str | None = None) -> dict:')

# chat
content = content.replace('def chat(email: str, password: str, course_id: str, activity_no: int, message: str) -> dict:', 'def chat(email: str, password: str | None = None, course_id: str = "", activity_no: int = 0, message: str = "", token: str | None = None) -> dict:')

with open('app/services.py', 'w') as f:
    f.write(content)

print("Student refactoring complete.")
