from sqlalchemy import Column, Integer, Text, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)

    rating = Column(Float, nullable=False)
    comment = Column(Text, nullable=True)

    create_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
    property = relationship("Property")