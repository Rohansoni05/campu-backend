from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field


class MaterialResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    subject_code: str
    branch: str
    semester: int
    section: str | None = None
    file_url: str
    uploaded_by: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class TimetableCreate(BaseModel):
    day: str
    start_time: str
    end_time: str
    subject_code: str
    subject_name: str
    teacher_id: int | None = None
    branch: str
    semester: int
    section: str | None = None
    room: str | None = None
    entry_type: str = "Lecture"


class TimetableResponse(TimetableCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class AttendanceItem(BaseModel):
    student_id: int
    subject_code: str
    date: date
    status: str = Field(pattern="^(present|absent)$")


class AttendanceSummary(BaseModel):
    subject_code: str
    present: int
    total: int
    percent: float


class StudentRosterItem(BaseModel):
    id: int
    name: str
    email: str
    enrollment_number: str | None = None
    department: str | None = None
    semester: int | None = None
    section: str | None = None
    model_config = ConfigDict(from_attributes=True)


class ProfileUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    semester: int | None = None
    section: str | None = None
    subject_codes: list[str] | None = None
    employee_id: str | None = None
