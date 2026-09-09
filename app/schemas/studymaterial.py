from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class StudyMaterialCreate(BaseModel):
    title: str
    description: Optional[str] = None

    emp_id: str
    subject_code: str

    classname: str
    branch: str
    semester: int
    section: Optional[str] = None

    pdf_url: str


class StudyMaterialResponse(BaseModel):
    id: int

    title: str
    description: Optional[str] = None

    emp_id: str
    subject_code: str

    classname: str
    branch: str
    semester: int
    section: Optional[str] = None

    pdf_url: str

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)