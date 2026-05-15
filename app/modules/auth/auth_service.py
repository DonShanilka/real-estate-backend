from sqlalchemy.orm import Session

from app.modules.users.user_model import User
from app.core.security import (hash_password, verify_password, create_access_token)

def register_user(db: Session, user_data):
    existing_user = db.query(User).filter(User.email == user_data.email).first()

    if existing_user:
        return None

    new_user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        password=hash_password(user_data.password),
        role=user_data.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

def login_user(db: Session, login_data):
    user = db.query(User).filter(User.email == login_data.email).first()

    if not user:
        return None

    if not verify_password(
        login_data.password,
        user.password
    ):
        return None

    token = create_access_token({
        "user_id": user.id,
        "role": user.role
    })

    return token