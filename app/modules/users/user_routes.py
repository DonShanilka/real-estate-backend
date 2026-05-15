from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal

from app.modules.users.user_service import (get_all_users, get_user_by_id, update_user, delete_user)
from app.modules.users.user_schema import (UserResponseSchema, UpdateUserSchema)

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

@router.get("/{user_id}")
def single_user(user_id: int, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user