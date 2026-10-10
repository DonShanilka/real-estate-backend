from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.modules.auth.auth_schema import (
    GoogleLoginSchema,
    LoginSchema,
    RegisterSchema,
)

from app.modules.auth.auth_service import (
    google_login_user,
    login_user,
    register_user,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

@router.post("/register")
def register(
    user: RegisterSchema,
    db: Session = Depends(get_db)
):
    new_user = register_user(db, user)

    if not new_user:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    return {
        "message": "User registered successfully"
    }

@router.post("/login")
def login(
    user: LoginSchema,
    db: Session = Depends(get_db)
):
    token = login_user(db, user)

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@router.post("/google")
def google_login(
    body: GoogleLoginSchema,
    db: Session = Depends(get_db),
):
    token = google_login_user(db, body.credential)
    return {"access_token": token, "token_type": "bearer"}
