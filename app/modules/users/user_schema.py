from pydantic import BaseModel, EmailStr
from typing import Optional

class UserResponseSchema(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    phone: Optional[str]
    role: str
    profile_image = Optional[str]
    
    is_actived: bool
    is_verified: bool
    
    class Config:
        from_attributes = True
        
        
    class UpdateUserSchema(BaseModel):
        full_name: Optional[str] = None
        phone: Optional[str] = None
        profile_image: Optional[str] = None