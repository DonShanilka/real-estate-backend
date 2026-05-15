from sqlalchemy import (Column, Integer, String, Text, Float, ForeignKey, DateTime, Enum)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class PropertyView(Base):
    __tablename__ = "property_views"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    property_id = Column(Integer, ForeignKey("properties.id"))

    viewed_at = Column(DateTime(timezone=True), server_default=func.now())