from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Fail fast if required env vars are missing
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_ROLE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
DATABASE_URL = os.environ["DATABASE_URL"]

from app.services import (
    studentLogin,
    setStudentPassword,
    changeStudentPassword,
    getActivity,
    logScore,
    chat,
    instructorLogin,
    setInstructorPassword,
    changeInstructorPassword,
    listMyCourses,
    listActivities,
    createActivity,
    updateActivity,
    startActivity,
    endActivity,
    exportScores,
    resetActivity,
    resetStudentPassword,
    gradeStudent,
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request body models
# ---------------------------------------------------------------------------

class StudentLoginBody(BaseModel):
    email: str
    password: str | None = None
    token: str | None = None

class SetStudentPasswordBody(BaseModel):
    email: str
    password: str | None = None

class ChangeStudentPasswordBody(BaseModel):
    email: str
    password: str
    new_password: str
    old_password: str

class GetActivityBody(BaseModel):
    email: str
    password: str | None = None
    course_id: str
    activity_no: int

class LogScoreBody(BaseModel):
    email: str
    password: str | None = None
    course_id: str
    activity_no: int
    score: float
    meta: str | None = None

class ChatBody(BaseModel):
    email: str
    password: str | None = None
    course_id: str
    activity_no: int
    message: str

class InstructorLoginBody(BaseModel):
    email: str
    password: str | None = None
    token: str | None = None

class SetInstructorPasswordBody(BaseModel):
    email: str
    password: str | None = None

class ChangeInstructorPasswordBody(BaseModel):
    email: str
    password: str
    old_password: str
    new_password: str

class ListMyCoursesBody(BaseModel):
    email: str
    password: str | None = None

class ListActivitiesBody(BaseModel):
    email: str
    password: str | None = None
    course_id: str

class CreateActivityBody(BaseModel):
    email: str
    password: str | None = None
    course_id: str
    activity_text: str
    learning_objectives: list[str]
    activity_no_optional: int | None = None

class UpdateActivityBody(BaseModel):
    email: str
    password: str | None = None
    course_id: str
    activity_no: int
    patch: dict[str, Any]

class ActivityActionBody(BaseModel):
    email: str
    password: str | None = None
    course_id: str
    activity_no: int

class ResetStudentPasswordBody(BaseModel):
    email: str
    password: str | None = None
    course_id: str
    student_email: str
    new_password: str

class ManualGradeBody(BaseModel):
    email: str
    password: str
    course_id: str
    activity_no: int
    student_email: str
    score: float
    meta: str | None = None


# ---------------------------------------------------------------------------
# Student endpoints
# ---------------------------------------------------------------------------

@app.post("/student/login")
def route_student_login(body: StudentLoginBody):
    return studentLogin(body.email, body.password, body.token)


@app.post("/student/set-password")
def route_set_student_password(body: SetStudentPasswordBody):
    return setStudentPassword(body.email, body.password)


@app.post("/student/change-password")
def route_change_student_password(body: ChangeStudentPasswordBody):
    return changeStudentPassword(body.email, body.password, body.new_password, body.old_password)


@app.post("/student/get-activity")
def route_get_activity(body: GetActivityBody):
    return getActivity(body.email, body.password, body.course_id, body.activity_no)


@app.post("/student/log-score")
def route_log_score(body: LogScoreBody):
    return logScore(body.email, body.password, body.course_id, body.activity_no, body.score, body.meta)


@app.post("/student/chat")
def route_chat(body: ChatBody):
    return chat(body.email, body.password, body.course_id, body.activity_no, body.message)


# ---------------------------------------------------------------------------
# Instructor endpoints
# ---------------------------------------------------------------------------

@app.post("/instructor/login")
def route_instructor_login(body: InstructorLoginBody):
    return instructorLogin(body.email, body.password, body.token)


@app.post("/instructor/set-password")
def route_set_instructor_password(body: SetInstructorPasswordBody):
    return setInstructorPassword(body.email, body.password)


@app.post("/instructor/change-password")
def route_change_instructor_password(body: ChangeInstructorPasswordBody):
    return changeInstructorPassword(body.email, body.password, body.old_password, body.new_password)


@app.post("/instructor/list-courses")
def route_list_my_courses(body: ListMyCoursesBody):
    return listMyCourses(body.email, body.password)


@app.post("/instructor/list-activities")
def route_list_activities(body: ListActivitiesBody):
    return listActivities(body.email, body.password, body.course_id)


@app.post("/instructor/create-activity")
def route_create_activity(body: CreateActivityBody):
    return createActivity(
        body.email,
        body.password,
        body.course_id,
        body.activity_text,
        body.learning_objectives,
        body.activity_no_optional,
    )


@app.post("/instructor/update-activity")
def route_update_activity(body: UpdateActivityBody):
    return updateActivity(body.email, body.password, body.course_id, body.activity_no, body.patch)


@app.post("/instructor/start-activity")
def route_start_activity(body: ActivityActionBody):
    return startActivity(body.email, body.password, body.course_id, body.activity_no)


@app.post("/instructor/end-activity")
def route_end_activity(body: ActivityActionBody):
    return endActivity(body.email, body.password, body.course_id, body.activity_no)


@app.post("/instructor/export-scores")
def route_export_scores(body: ActivityActionBody):
    return exportScores(body.email, body.password, body.course_id, body.activity_no)


@app.post("/instructor/reset-activity")
def route_reset_activity(body: ActivityActionBody):
    return resetActivity(body.email, body.password, body.course_id, body.activity_no)


@app.post("/instructor/reset-student-password")
def route_reset_student_password(body: ResetStudentPasswordBody):
    return resetStudentPassword(
        body.email,
        body.password,
        body.course_id,
        body.student_email,
        body.new_password,
    )


@app.post("/instructor/manual-grade")
def route_manual_grade(body: ManualGradeBody):
    return gradeStudent(
        body.email,
        body.password,
        body.course_id,
        body.activity_no,
        body.student_email,
        body.score,
        body.meta,
    )
