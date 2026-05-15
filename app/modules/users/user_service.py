from sqlalchemy.orm import Session
from app.modules.users.user_model import User

def get_all_users(db: Session):
    return db.query(User).all()

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def update_user(db: Session, user_id: int, user_data):
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        return None
    
    if user_data.phone:
        user.phone = user_data.phone
        
    if user_data.profile_image:
        user.profile_image = user_data.profile_image
        
    db.commit()
    db.refresh(user)
    
def delete_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).filter()
    
    if not user:
        return None
    
    db.delete(user)
    db.commit()
    
    return True