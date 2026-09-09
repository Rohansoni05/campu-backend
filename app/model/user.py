from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.dialects.postgresql import ARRAY

from app.database import Base


class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String,
        nullable=False
    )

    email = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    password = Column(
        String,
        nullable=False
    )

    role = Column(
        String,
        nullable=False,
        default="student"
    )

    department = Column(
        String,
        nullable=True
    )

    semester = Column(
        Integer,
        nullable=True
    )

    section = Column(
        String,
        nullable=True
    )

    employee_id = Column(
        String,
        nullable=True
    )

    enrollment_number = Column(
        String,
        nullable=True
    )

    subject_codes = Column(
        ARRAY(String),
        default=list
    )

    is_active = Column(
        Boolean,
        default=True
    )