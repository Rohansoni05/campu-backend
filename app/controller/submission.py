from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.assignment import Assignment
from app.models.submission import Submission
from app.schemas.submission import SubmissionGrade


def create_submission(
    db: Session,
    assignment_id: int,
    student_id: str,
    file_url: str
):

    assignment = db.scalar(
        select(Assignment).where(
            Assignment.id == assignment_id
        )
    )

    if not assignment:
        raise ValueError(
            "Assignment not found"
        )

    existing_submission = db.scalar(
        select(Submission).where(
            Submission.assignment_id == assignment_id,
            Submission.student_id == student_id
        )
    )

    if existing_submission:
        raise ValueError(
            "You have already submitted this assignment"
        )

    if datetime.now() > assignment.last_date_of_submission:
        raise ValueError(
            "Submission deadline has passed"
        )

    submission = Submission(
        assignment_id=assignment_id,
        student_id=student_id,
        file_url=file_url,
        status="submitted"
    )

    db.add(submission)

    db.commit()

    db.refresh(submission)

    return submission


def get_submission(
    db: Session,
    submission_id: int
):

    return db.scalar(
        select(Submission).where(
            Submission.id == submission_id
        )
    )


def get_student_submission(
    db: Session,
    assignment_id: int,
    student_id: str
):

    return db.scalar(
        select(Submission).where(
            Submission.assignment_id == assignment_id,
            Submission.student_id == student_id
        )
    )


def get_assignment_submissions(
    db: Session,
    assignment_id: int
):

    statement = select(Submission).where(
        Submission.assignment_id == assignment_id
    ).order_by(
        Submission.submitted_at.desc()
    )

    return db.scalars(statement).all()


def grade_submission(
    db: Session,
    submission: Submission,
    data: SubmissionGrade
):

    submission.marks = data.marks
    submission.feedback = data.feedback
    submission.status = "graded"

    db.commit()

    db.refresh(submission)

    return submission