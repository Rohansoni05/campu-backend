from datetime import date, datetime
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import Integer, func
from sqlalchemy.orm import Session

from app.database import get_db
from app.model.academic import AttendanceRecord, StudyMaterial, TimetableEntry
from app.model.user import User
from app.schemas.academic import (
    AttendanceItem,
    AttendanceSummary,
    MaterialResponse,
    StudentRosterItem,
    TimetableCreate,
    TimetableResponse,
)
from app.utils.auth import get_current_user

router = APIRouter(tags=["Academics"])
UPLOAD_DIR = Path("uploads/materials")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def require_staff(user: User):
    if user.role not in {"teacher", "hod"}:
        raise HTTPException(status_code=403, detail="Teacher or HOD access required")


def require_hod(user: User):
    if user.role != "hod":
        raise HTTPException(status_code=403, detail="HOD access required")


def student_scope(user: User):
    return (user.department, user.semester, user.section)


@router.get("/materials", response_model=list[MaterialResponse])
def list_materials(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(StudyMaterial)
    if current_user.role == "student":
        branch, semester, section = student_scope(current_user)
        query = query.filter(StudyMaterial.branch == branch, StudyMaterial.semester == semester)
        if section:
            query = query.filter((StudyMaterial.section == section) | (StudyMaterial.section.is_(None)))
    return query.order_by(StudyMaterial.created_at.desc()).all()


@router.post("/materials", response_model=MaterialResponse)
async def upload_material(
    title: str = Form(...),
    description: str | None = Form(None),
    subject_code: str = Form(...),
    branch: str = Form(...),
    semester: int = Form(...),
    section: str | None = Form(None),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_staff(current_user)
    if not file.filename:
        raise HTTPException(status_code=400, detail="A file is required")
    extension = Path(file.filename).suffix.lower()
    if extension not in {".pdf", ".doc", ".docx", ".ppt", ".pptx", ".zip"}:
        raise HTTPException(status_code=400, detail="Unsupported material file type")
    filename = f"{uuid4()}{extension}"
    (UPLOAD_DIR / filename).write_bytes(await file.read())
    material = StudyMaterial(
        title=title, description=description, subject_code=subject_code,
        branch=branch, semester=semester, section=section,
        file_url=f"/uploads/materials/{filename}", uploaded_by=current_user.id,
    )
    db.add(material)
    db.commit()
    db.refresh(material)
    return material


@router.get("/timetable", response_model=list[TimetableResponse])
def list_timetable(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(TimetableEntry)
    if current_user.role == "student":
        branch, semester, section = student_scope(current_user)
        normalized_branch = (branch or "").strip().lower()
        query = query.filter(func.lower(func.trim(TimetableEntry.branch)) == normalized_branch, TimetableEntry.semester == semester)
        if section:
            normalized_section = section.strip().lower()
            query = query.filter((func.lower(func.trim(TimetableEntry.section)) == normalized_section) | (TimetableEntry.section.is_(None)))
    elif current_user.role == "teacher":
        query = query.filter(TimetableEntry.teacher_id == current_user.id)
    return query.order_by(TimetableEntry.day, TimetableEntry.start_time).all()


@router.post("/timetable", response_model=TimetableResponse)
def create_timetable(
    data: TimetableCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_staff(current_user)
    values = data.model_dump()
    if current_user.role == "teacher":
        values["teacher_id"] = current_user.id
    entry = TimetableEntry(**values)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.post("/timetable/week", response_model=list[TimetableResponse])
def create_week_timetable(
    data: list[TimetableCreate],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_hod(current_user)
    if {entry.day for entry in data} != {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday"}:
        raise HTTPException(status_code=400, detail="A weekly timetable must contain Monday through Friday")
    entries = [TimetableEntry(**entry.model_dump()) for entry in data]
    try:
        db.add_all(entries)
        db.commit()
        for entry in entries:
            db.refresh(entry)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Unable to publish the weekly timetable")
    return entries


@router.delete("/timetable/{entry_id}")
def delete_timetable(entry_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_hod(current_user)
    entry = db.get(TimetableEntry, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Timetable entry not found")
    db.delete(entry)
    db.commit()
    return {"message": "Timetable entry deleted"}


@router.post("/attendance")
def mark_attendance(
    items: list[AttendanceItem],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_staff(current_user)
    for item in items:
        student = db.get(User, item.student_id)
        if not student or student.role != "student":
            raise HTTPException(status_code=404, detail=f"Student {item.student_id} not found")
        if current_user.department and (student.department or "").strip().lower() != current_user.department.strip().lower():
            raise HTTPException(status_code=403, detail="You can only mark attendance for students in your department")
        if current_user.role == "teacher" and item.subject_code.upper() not in {code.upper() for code in (current_user.subject_codes or [])}:
            raise HTTPException(status_code=403, detail="You can only mark attendance for your assigned subjects")
        existing = db.query(AttendanceRecord).filter_by(
            student_id=item.student_id, subject_code=item.subject_code, date=item.date
        ).first()
        if existing:
            existing.status = item.status
            existing.marked_by = current_user.id
        else:
            db.add(AttendanceRecord(**item.model_dump(), marked_by=current_user.id))
    db.commit()
    return {"message": f"Attendance saved for {len(items)} students"}


@router.get("/attendance/roster", response_model=list[StudentRosterItem])
def attendance_roster(
    subject_code: str,
    semester: int | None = None,
    section: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_staff(current_user)
    subject_code = subject_code.strip().upper()
    if current_user.role == "teacher" and subject_code not in {code.upper() for code in (current_user.subject_codes or [])}:
        raise HTTPException(status_code=403, detail="You can only access rosters for your assigned subjects")
    query = db.query(User).filter(User.role == "student")
    if current_user.department:
        query = query.filter(func.lower(func.trim(User.department)) == current_user.department.strip().lower())
    if semester:
        query = query.filter(User.semester == semester)
    if section:
        query = query.filter(func.lower(func.trim(User.section)) == section.strip().lower())
    query = query.filter(User.subject_codes.any(subject_code))
    return query.order_by(User.name).all()


@router.get("/attendance/me", response_model=list[AttendanceSummary])
def my_attendance(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Student access required")
    rows = db.query(
        AttendanceRecord.subject_code,
        func.sum(func.cast(AttendanceRecord.status == "present", Integer)).label("present"),
        func.count(AttendanceRecord.id).label("total"),
    ).filter(AttendanceRecord.student_id == current_user.id).group_by(AttendanceRecord.subject_code).all()
    return [AttendanceSummary(subject_code=code, present=present or 0, total=total, percent=round((present or 0) * 100 / total, 1)) for code, present, total in rows]
