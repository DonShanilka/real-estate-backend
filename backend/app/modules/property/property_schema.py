from pydantic import BaseModel
from typing import Optional
from enum import Enum


class PropertyType(str, Enum):
    APARTMENT = "APARTMENT"
    HOUSE = "HOUSE"
    LAND = "LAND"
    VILLA = "VILLA"


class PropertyStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    SOLD = "SOLD"
    RENTED = "RENTED"


class PropertyCreateSchema(BaseModel):
    title: str
    description: Optional[str] = None
    price: float

    property_type: PropertyType
    status: PropertyStatus = PropertyStatus.AVAILABLE

    bedrooms: int
    bathrooms: int
    area_size: float

    address: str
    city: str
    district: str
    country: str

    latitude: Optional[float] = None
    longitude: Optional[float] = None

    owner_id: int

    image_url: str
    video_url: str


class PropertyUpdateSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None

    property_type: Optional[PropertyType] = None
    status: Optional[PropertyStatus] = None

    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    area_size: Optional[float] = None

    address: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    country: Optional[str] = None

    latitude: Optional[float] = None
    longitude: Optional[float] = None

    image_url: Optional[str] = None
    video_url: Optional[str] = None