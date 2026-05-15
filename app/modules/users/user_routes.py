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
    
    