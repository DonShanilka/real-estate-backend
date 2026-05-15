from sqlalchemy import (Column, Integer, String, Text, Float, ForeignKey, DateTime, Enum, Boolean)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)

    title = Column(String(255))
    message = Column(Text)

    is_read = Column(Boolean, default=False)

    user_id = Column(Integer, ForeignKey("users.id"))

    created_at = Column(DateTime(timezone=True), server_default=func.now())