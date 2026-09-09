from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile


BASE_UPLOAD_DIR = Path("uploads")

ASSIGNMENT_DIR = BASE_UPLOAD_DIR / "assignments"
SUBMISSION_DIR = BASE_UPLOAD_DIR / "submissions"


ASSIGNMENT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

SUBMISSION_DIR.mkdir(
    parents=True,
    exist_ok=True
)


async def save_assignment_pdf(
    file: UploadFile
) -> str:

    if file.content_type != "application/pdf":
        raise ValueError(
            "Only PDF files are allowed"
        )

    filename = f"{uuid4()}.pdf"

    path = ASSIGNMENT_DIR / filename

    content = await file.read()

    with open(path, "wb") as buffer:
        buffer.write(content)

    return f"/uploads/assignments/{filename}"


async def save_submission_pdf(
    file: UploadFile
) -> str:

    if file.content_type != "application/pdf":
        raise ValueError(
            "Only PDF files are allowed"
        )

    filename = f"{uuid4()}.pdf"

    path = SUBMISSION_DIR / filename

    content = await file.read()

    with open(path, "wb") as buffer:
        buffer.write(content)

    return f"/uploads/submissions/{filename}"