from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.assignment import Assignment
from app.schemas.assignment import AssignmentCreate


def create_assignment(
    db: Session,
    data: AssignmentCreate,
    pdf_url: str | None
):

    assignment = Assignment(
        title=data.title,
        description=data.description,

        subject_code=data.subject_code,
        emp_id=data.emp_id,

        classname=data.classname,
        branch=data.branch,
        semester=data.semester,
        section=data.section,

        last_date_of_submission=data.last_date_of_submission,

        pdf_url=pdf_url
    )

    db.add(assignment)

    db.commit()

    db.refresh(assignment)

    return assignment


def get_assignment(
    db: Session,
    assignment_id: int
):

    statement = select(Assignment).where(
        Assignment.id == assignment_id
    )

    return db.scalar(statement)


def get_assignments(
    db: Session,
    branch: str | None = None,
    semester: int | None = None,
    section: str | None = None,
    subject_code: str | None = None,
):

    statement = select(Assignment)

    if branch:
        statement = statement.where(
            Assignment.branch == branch
        )

    if semester:
        statement = statement.where(
            Assignment.semester == semester
        )

    if section:
        statement = statement.where(
            Assignment.section == section
        )

    if subject_code:
        statement = statement.where(
            Assignment.subject_code == subject_code
        )

    statement = statement.order_by(
        Assignment.created_at.desc()
    )

    return db.scalars(statement).all()


def delete_assignment(
    db: Session,
    assignment: Assignment
):

    db.delete(assignment)

    db.commit()