from fastapi import APIRouter
from app.schemas import Student

router = APIRouter()


@router.get("/")
def get_students():
    return {
        "students": []
    }


@router.post("/")
def create_student(student: Student):
    return {
        "message": "Student received",
        "student": student
    }