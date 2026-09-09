from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.model.assignment import Assignment
from app.model.user import User
from app.schemas.assignment import AssignmentResponse
from app.services.storage_service import save_assignment_pdf
from app.utils.auth import get_current_user

router = APIRouter(prefix="/assignments", tags=["Assignments"])


def require_staff(user: User):
    if user.role not in {"teacher", "hod"}:
        raise HTTPException(status_code=403, detail="Teacher or HOD access required")


@router.post("/", response_model=AssignmentResponse)
async def create_assignment_route(
    title: str = Form(..., description="Assignment title"),
    description: str | None = Form(None, description="Instructions or assignment details"),
    subject_code: str = Form(..., description="Subject code, for example CS301"),
    classname: str = Form(..., description="Class or course name"),
    branch: str = Form(..., description="Department/branch visible to students"),
    semester: int = Form(..., ge=1, description="Target semester"),
    section: str | None = Form(None, description="Target section; omit for all sections"),
    last_date_of_submission: datetime = Form(..., description="Submission deadline in ISO format"),
    pdf: UploadFile | None = File(None), current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_staff(current_user)
    title = title.strip()
    subject_code = subject_code.strip().upper()
    classname = classname.strip()
    branch = branch.strip()
    section = section.strip() if section else None
    if not title or not subject_code or not classname or not branch:
        raise HTTPException(status_code=422, detail="Title, subject code, class name, and branch are required")

    try:
        pdf_url = await save_assignment_pdf(pdf) if pdf else None
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    assignment = Assignment(
        title=title, description=description, subject_code=subject_code,
        emp_id=current_user.employee_id or str(current_user.id), classname=classname,
        branch=branch, semester=semester, section=section,
        last_date_of_submission=last_date_of_submission, pdf_url=pdf_url,
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


@router.get("/", response_model=list[AssignmentResponse])
def list_assignments(
    branch: str | None = None, semester: int | None = None, section: str | None = None,
    subject_code: str | None = None, current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Assignment)
    if current_user.role == "student":
        branch, semester, section = current_user.department, current_user.semester, current_user.section
        staff_users = db.query(User).filter(User.role.in_(["teacher", "hod"])).all()
        staff_ids = [identifier for staff_user in staff_users for identifier in (staff_user.employee_id, str(staff_user.id)) if identifier]
        query = query.filter(Assignment.emp_id.in_(staff_ids))
    if branch:
        query = query.filter(func.lower(func.trim(Assignment.branch)) == branch.strip().lower())
    if semester:
        query = query.filter(Assignment.semester == semester)
    if section:
        query = query.filter((func.lower(func.trim(Assignment.section)) == section.strip().lower()) | (Assignment.section.is_(None)))
    if subject_code:
        query = query.filter(Assignment.subject_code == subject_code)
    return query.order_by(Assignment.created_at.desc()).all()


@router.delete("/{assignment_id}")
def delete_assignment_route(assignment_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_staff(current_user)
    assignment = db.get(Assignment, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    db.delete(assignment)
    db.commit()
    return {"message": "Assignment deleted successfully"}
