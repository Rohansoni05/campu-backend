# app/schemas/assignment.py

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AssignmentCreate(BaseModel):
    title: str
    description: Optional[str] = None

    subject_code: str
    emp_id: str

    classname: str
    branch: str
    semester: int
    section: Optional[str] = None

    last_date_of_submission: datetime


class AssignmentResponse(BaseModel):
    id: int

    title: str
    description: Optional[str] = None

    subject_code: str
    emp_id: str

    classname: str
    branch: str
    semester: int
    section: Optional[str] = None

    last_date_of_submission: datetime

    pdf_url: Optional[str] = None

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)