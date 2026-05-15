from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class UserRole(enum.Enum):
    ADMIN = "ADMIN"
    AGENT = "AGENT"
    OWNER = "OWNER"
    BUYER = "BUYER"
    
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    phone = Column(String(20))
    password = Column(String(255), nullable=False)
    
    role = Column(Enum(UserRole), default=UserRole.BUYER)
    
    profile_image = Column(String(255))
    
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())