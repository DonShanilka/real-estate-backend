from pydantic import BaseModel, Field


class PricePredictionRequest(BaseModel):
    city: str = Field(min_length=2, max_length=100)
    district: str | None = Field(default=None, max_length=100)
    country: str = Field(default="Sri Lanka", min_length=2, max_length=100)
    property_type: str = Field(min_length=2, max_length=40)
    bedrooms: int = Field(ge=0, le=20)
    bathrooms: int = Field(ge=0, le=20)
    house_area_sqft: float | None = Field(default=None, gt=0, le=100_000)
    land_area_perches: float | None = Field(default=None, gt=0, le=500)
