from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal

from app.modules.users.user_service import (get_all_users, get_user_by_id, update_user, delete_user)
from app.modules.users.user_schema import (UserResponseSchema, UpdateUserSchema)
from app.core.security import get_current_user
from app.modules.users.user_model import User, UserRole


router = APIRouter(prefix="/users", tags=["Users"])

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.get("/")
def users(db: Session = Depends(get_db)):
    return get_all_users(db)


@router.get("/agents")
def agents(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    actor = db.query(User).filter(User.id == current_user["id"]).first()
    if not actor or not actor.is_active:
        raise HTTPException(status_code=401, detail="Authenticated user not found")
    rows = (
        db.query(User.id, User.full_name, User.email, User.phone, User.profile_image)
        .filter(User.role == UserRole.AGENT, User.is_active.is_(True))
        .order_by(User.full_name.asc())
        .all()
    )
    return [
        {
            "id": row.id,
            "full_name": row.full_name,
            "email": row.email,
            "phone": row.phone,
            "profile_image": row.profile_image,
        }
        for row in rows
    ]


@router.get("/{user_id}")
def single_user(user_id: int, db: Session = Depends(get_db)):

    user = get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.put("/{user_id}")
def update_single_user(user_id: int, user_data: UpdateUserSchema, db: Session = Depends(get_db)):
    user = update_user(db, user_id, user_data)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "message": "User updated successfully",
        "data": user
    }


@router.delete("/{user_id}")
def remove_user(user_id: int, db: Session = Depends(get_db)):

    deleted = delete_user(db, user_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "message": "User deleted successfully"
    }


