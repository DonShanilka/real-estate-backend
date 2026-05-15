from pydantic import BaseModel
from typing import Optional


class PropertyCreateSchema(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    location: str
    bedrooms: int
    bathrooms: int
    area: float
    property_type: str
    owner_id: int


class PropertyUpdateSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    location: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    area: Optional[float] = None
    status: Optional[str] = None
    image: Optional[str] = None
