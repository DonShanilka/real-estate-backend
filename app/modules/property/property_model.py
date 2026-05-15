from sqlalchemy import (Column, Integer, String, Text, Float, ForeignKey, DateTime, Enum)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class PropertyStatus(enum.Enum):
    AVAILABLE = "AVAILABLE"
    SOLD = "SOLD"
    RENTED = "RENTED"
    
class PropertyType(enum.Enum):
    APARTMENT = "APARTMENT"
    HOUSE = "HOUSE"
    LAND = "LAND"
    VILLA = "VILLA"
    
class Property(Base):
    __tablename__ = "properties"
    
    id = Column(Integer, primary_key=True, index=True)
    
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    price = Column(Float, nullable=False)
    
    property_tyoe = Column(Enum(PropertyType))
    status = Column(Enum(PropertyStatus), default=PropertyStatus.AVAILABLE)
    
    beadrooms = Column(Integer)
    bathrooms = Column(Integer)
    area_size = Column(Float)
    
    address = Column(String(255))
    city = Column(String(100))
    district = Column(String(100))
    country = Column(String(100))
    
    latitude = Column(Float)
    longitude = Column(Float)
    
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    create_at = Column(DateTime(timezone=True), server_default=func.now())
    
    owner = relationship("User")
    