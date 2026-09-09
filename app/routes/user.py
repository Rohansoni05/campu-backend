from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.user import (
    UserCreate,
    UserResponse,
    LoginRequest,
    LoginResponse
)

from app.controller.user_controller import (
    register_user,
    login_user
)

from app.utils.auth import get_current_user
from app.schemas.academic import ProfileUpdate
from app.model.user import User


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# =====================================
# REGISTER
# =====================================

@router.post(
    "/register",
    response_model=UserResponse
)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):

    return register_user(
        user_data,
        db
    )


# =====================================
# LOGIN
# =====================================

@router.post(
    "/login",
    response_model=LoginResponse
)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):

    return login_user(
        login_data,
        db
    )


# =====================================
# CURRENT USER
# =====================================

@router.get(
    "/me",
    response_model=UserResponse
)
def get_me(
    current_user = Depends(
        get_current_user
    )
):

    return current_user


@router.patch("/me", response_model=UserResponse)
def update_me(
    updates: ProfileUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    values = updates.model_dump(exclude_unset=True)
    if "email" in values:
        existing = db.query(User).filter(User.email == values["email"], User.id != current_user.id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
    for key, value in values.items():
        setattr(current_user, key, value)
    db.commit()
    db.refresh(current_user)
    return current_user