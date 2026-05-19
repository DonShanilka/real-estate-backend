from pydantic import BaseModel
from typing import Optional

class ReviewCreate(BaseModel):
    
    property_id: int
    reating: float
    comment: Optional[str] = None
    
    
class ReviewUpdate(BaseModel):
    
    rating: Optional[float] = None
    comment: Optional[str] = None