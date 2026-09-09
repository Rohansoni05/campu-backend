from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SubmissionResponse(BaseModel):

    id: int

    assignment_id: int

    student_id: str

    file_url: str

    submitted_at: datetime

    status: str

    marks: int | None = None

    feedback: str | None = None

    model_config = ConfigDict(
        from_attributes=True
    )


class SubmissionGrade(BaseModel):

    marks: int

    feedback: str | None = None