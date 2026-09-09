from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class PreviousYearPaperCreate(BaseModel):
    title: str

    subject_code: str
    subject_name: str

    year: int
    semester: int

    classname: Optional[str] = None
    branch: Optional[str] = None

    emp_id: Optional[str] = None

    pdf_url: str

    description: Optional[str] = None


class PreviousYearPaperResponse(BaseModel):
    id: int

    title: str

    subject_code: str
    subject_name: str

    year: int
    semester: int

    classname: Optional[str] = None
    branch: Optional[str] = None

    emp_id: Optional[str] = None

    pdf_url: str

    description: Optional[str] = None

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)