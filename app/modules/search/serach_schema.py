from pydantic import BaseModel
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