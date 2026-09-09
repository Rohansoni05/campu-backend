from pydantic import BaseModel, EmailStr, ConfigDict, Field, model_validator
from typing import Literal, Optional


class UserCreate(BaseModel):

    name: str
    email: EmailStr
    password: str

    role: Literal["student", "teacher", "hod"] = "student"

    department: Optional[str] = None
    semester: Optional[int] = None
    section: Optional[str] = None

    employee_id: Optional[str] = None
    enrollment_number: Optional[str] = None

    subject_codes: list[str] = Field(
        default_factory=list
    )

    @model_validator(mode="after")
    def validate_student_profile(self):
        if self.role == "student":
            required = {
                "department": self.department,
                "semester": self.semester,
                "section": self.section,
                "enrollment_number": self.enrollment_number,
                "subject_codes": self.subject_codes,
            }
            missing = [name for name, value in required.items() if not value]
            if missing:
                raise ValueError(f"Students must complete: {', '.join(missing)}")
        return self


class UserResponse(BaseModel):

    id: int
    name: str
    email: EmailStr
    role: str

    department: Optional[str] = None
    semester: Optional[int] = None
    section: Optional[str] = None

    employee_id: Optional[str] = None
    enrollment_number: Optional[str] = None

    subject_codes: list[str] = Field(
        default_factory=list
    )

    is_active: bool

    model_config = ConfigDict(
        from_attributes=True
    )


class LoginRequest(BaseModel):

    email: EmailStr
    password: str


class LoginResponse(BaseModel):

    access_token: str
    token_type: str
    user: UserResponse