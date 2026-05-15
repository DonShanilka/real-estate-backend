from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserResponseSchema(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    role: str

    profile_image: Optional[str] = None

    is_active: bool
    is_verified: bool

    created_at: datetime

    class Config:
        from_attributes = True


class UpdateUserSchema(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    profile_image: Optional[str] = None