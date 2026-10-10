import secrets

from fastapi import HTTPException
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import GOOGLE_CLIENT_ID
from app.core.security import create_access_token, hash_password, verify_password
from app.modules.auth.google_identity_model import GoogleIdentity
from app.modules.users.user_model import User, UserRole


def register_user(db: Session, user_data):
    existing_user = db.query(User).filter(
        User.email == user_data.email
    ).first()

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
    user = db.query(User).filter(
        User.email == login_data.email
    ).first()

    if not user:
        return None

    if not verify_password(login_data.password, user.password):
        return None

    token = create_access_token({
        "user_id": user.id,
        "role": user.role.value
    })

    return token


def google_login_user(db: Session, credential: str):
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=503, detail="Google sign-in is not configured")

    try:
        claims = id_token.verify_oauth2_token(
            credential, google_requests.Request(), GOOGLE_CLIENT_ID
        )
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Invalid Google credential") from exc

    google_sub = claims.get("sub")
    email = (claims.get("email") or "").strip().lower()
    if not google_sub or not email or claims.get("email_verified") is not True:
        raise HTTPException(status_code=401, detail="Google account email is not verified")

    identity = db.query(GoogleIdentity).filter(
        GoogleIdentity.google_sub == google_sub
    ).first()
    user = db.query(User).filter(User.id == identity.user_id).first() if identity else None

    if not user:
        user = db.query(User).filter(User.email == email).first()
        if user:
            # Only link an existing account when Google is authoritative for its email.
            is_authoritative_email = email.endswith("@gmail.com") or bool(claims.get("hd"))
            if not is_authoritative_email:
                raise HTTPException(
                    status_code=409,
                    detail="This email already has an account. Sign in with your password first.",
                )
        else:
            user = User(
                full_name=(claims.get("name") or email.split("@", 1)[0])[:150],
                email=email,
                password=hash_password(secrets.token_urlsafe(48)),
                role=UserRole.BUYER,
                profile_image=(claims.get("picture") or "")[:255] or None,
                is_verified=True,
            )
            db.add(user)
            try:
                db.commit()
                db.refresh(user)
            except IntegrityError:
                db.rollback()
                user = db.query(User).filter(User.email == email).first()
                if not user:
                    raise HTTPException(status_code=409, detail="Could not create Google account")

        if not identity:
            identity = GoogleIdentity(google_sub=google_sub, user_id=user.id)
            db.add(identity)
            try:
                db.commit()
            except IntegrityError:
                db.rollback()
                identity = db.query(GoogleIdentity).filter(
                    GoogleIdentity.google_sub == google_sub
                ).first()
                if not identity:
                    raise HTTPException(status_code=409, detail="Google account is already linked")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="This account is disabled")

    return create_access_token({"user_id": user.id, "role": user.role.value})
