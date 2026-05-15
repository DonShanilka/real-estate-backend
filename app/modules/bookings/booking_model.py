from sqlalchemy import (Column, Integer, String, Text, Float, ForeignKey, DateTime, Enum, Date)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True)
    
    booking_date_time = Column(DateTime)
    
    status = Column(String(50), default="PENDING")
    
    user_id = Column(Integer, ForeignKey("users.id"))
    property_id = Column(Integer, ForeignKey("properties.id"))
    
    user = relationship("User")
    property = relationship("Property")
    
    