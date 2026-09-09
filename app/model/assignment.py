from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from app.database import Base


class Assignment(Base):

    __tablename__ = "assignments"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    title = Column(
        String(255),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    subject_code = Column(
        String(50),
        nullable=False,
        index=True
    )

    emp_id = Column(
        String(50),
        nullable=False,
        index=True
    )

    classname = Column(
        String(100),
        nullable=False
    )

    branch = Column(
        String(100),
        nullable=False,
        index=True
    )

    semester = Column(
        Integer,
        nullable=False,
        index=True
    )

    section = Column(
        String(20),
        nullable=True,
        index=True
    )

    last_date_of_submission = Column(
        DateTime,
        nullable=False,
        index=True
    )

    pdf_url = Column(
        String(500),
        nullable=True
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )