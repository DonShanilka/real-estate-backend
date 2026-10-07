from pydantic import BaseModel, Field
from typing import Optional


class SearchQuery(BaseModel):

    keyword: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    property_type: Optional[str] = None

    min_price: Optional[float] = None
    max_price: Optional[float] = None

    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None

    min_area: Optional[float] = None
    max_area: Optional[float] = None

    sort: Optional[str] = "latest"

    page: int = 1
    limit: int = 10


class NaturalSearchRequest(BaseModel):
    query: str = Field(min_length=3, max_length=500)


class NearbySearchQuery(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    radius_km: float = Field(default=10, gt=0, le=500)
    limit: int = Field(default=50, ge=1, le=100)
