from pydantic import BaseModel
from typing import Optional


class ReviewCreate(BaseModel):

    rating: float
    comment: Optional[str] = None


class ReviewUpdate(BaseModel):

    rating: Optional[float] = None
    comment: Optional[str] = None


class ReviewResponse(BaseModel):

    id: int
    user_id: int
    property_id: int
    rating: float
    comment: Optional[str]

    class Config:
        from_attributes = True