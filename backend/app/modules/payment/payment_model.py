from sqlalchemy import (Column, Integer, String, Text, Float, ForeignKey, DateTime, Enum)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)

    amount = Column(Float, nullable=False)

    payment_method = Column(String(50))
    payment_status = Column(String(50), default="PENDING")

    transaction_id = Column(String(255))

    booking_id = Column(Integer, ForeignKey("bookings.id"))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    booking = relationship("Booking")