from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import engine, Base

# Models
from app.model.user import User
from app.model.assignment import Assignment
from app.model.submission import Submission
from app.model.academic import StudyMaterial, TimetableEntry, AttendanceRecord

# Routes
from app.routes.user import router as user_router
from app.routes.assignment import router as assignment_router
from app.routes.academic import router as academic_router


# ==============================
# DATABASE TABLES
# ==============================

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="CampusGPT API",
    description="Backend API for CampusGPT",
    version="1.0.0",
)


# ==============================
# CORS
# ==============================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173",
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ==============================
# STATIC FILES
# ==============================

app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads",
)


# ==============================
# ROUTES
# ==============================

app.include_router(user_router)

app.include_router(assignment_router)

app.include_router(academic_router)


# ==============================
# ROOT
# ==============================

@app.get("/")
def root():

    return {
        "message": "CampusGPT backend is running"
    }


# ==============================
# TEST
# ==============================

@app.get("/api/test")
def test():

    return {
        "success": True,
        "message": "API works"
    }


# ==============================
# DATABASE TEST
# ==============================

@app.get("/api/test-db")
def test_database():

    try:

        with engine.connect():

            return {
                "success": True,
                "message": "PostgreSQL connected"
            }

    except Exception as error:

        print("DATABASE ERROR:", error)

        return {
            "success": False,
            "message": "PostgreSQL connection failed",
            "error": str(error)
        }