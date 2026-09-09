from pydantic import BaseModel
from datetime import date


class StudentAttendance(BaseModel):
    enr: str
    attendance: str


class AttendanceCreate(BaseModel):
    classname: str
    branch: str
    date: date
    students: list[StudentAttendance]


class AttendanceResponse(BaseModel):
    id: int
    classname: str
    branch: str
    date: date
    students: list[StudentAttendance]