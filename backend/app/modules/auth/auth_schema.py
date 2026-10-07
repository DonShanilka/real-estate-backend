from pydantic import BaseModel, EmailStr
from app.modules.users.user_model import UserRole


class RegisterSchema(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: UserRole   


class LoginSchema(BaseModel):
    email: EmailStr
    password: str