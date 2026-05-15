from sqlalchemy import (Column, Integer, String, Text, Float, ForeignKey, DateTime, Enum)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True)
    
    rating = Column(Integer)
    comment = Column(Text)
    
    user_id = Column(Integer, ForeignKey("users.id"))
    property_id = Column(Integer, ForeignKey("properties.id"))
    
    user = relationship("User")
    property = relationship("property")