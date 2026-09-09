from pydantic import BaseModel, ConfigDict
from datetime import time


class TimetableSlot(BaseModel):
    start_time: time
    end_time: time
    teacher_name: str
    subject_code: str
    day: str


class TimetableSubject(BaseModel):
    subject: str
    slots: list[TimetableSlot]


class TimetableResponse(BaseModel):
    department: str
    subjects: list[TimetableSubject]

    model_config = ConfigDict(from_attributes=True)