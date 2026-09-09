from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.model.user import User

from app.schemas.user import (
    UserCreate,
    LoginRequest,
    LoginResponse
)

from app.utils.auth import (
    hash_password,
    verify_password,
    create_access_token
)


def register_user(
    user_data: UserCreate,
    db: Session
):

    # Check existing email
    existing_user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )


    # Create user
    new_user = User(

        name=user_data.name,

        email=user_data.email,

        password=hash_password(
            user_data.password
        ),

        role=user_data.role,

        department=user_data.department,

        semester=user_data.semester,

        section=user_data.section,

        employee_id=user_data.employee_id,

        enrollment_number=user_data.enrollment_number,

        subject_codes=user_data.subject_codes,

        is_active=True
    )


    db.add(new_user)

    db.commit()

    db.refresh(new_user)

    return new_user


def login_user(
    login_data: LoginRequest,
    db: Session
):

    user = (
        db.query(User)
        .filter(User.email == login_data.email)
        .first()
    )

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        login_data.password,
        user.password
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not user.is_active:

        raise HTTPException(
            status_code=403,
            detail="User account is inactive"
        )

    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role
    }

    access_token = create_access_token(
        token_data
    )

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=user
    )