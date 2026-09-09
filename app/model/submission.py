from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.sql import func

from app.database import Base


class Submission(Base):

    __tablename__ = "submissions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    assignment_id = Column(
        Integer,
        ForeignKey("assignments.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    student_id = Column(
        String(50),
        nullable=False,
        index=True
    )

    file_url = Column(
        String(500),
        nullable=False
    )

    submitted_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    status = Column(
        String(30),
        nullable=False,
        default="submitted"
    )

    marks = Column(
        Integer,
        nullable=True
    )

    feedback = Column(
        Text,
        nullable=True
    )

    __table_args__ = (
        UniqueConstraint(
            "assignment_id",
            "student_id",
            name="unique_student_assignment"
        ),
    )