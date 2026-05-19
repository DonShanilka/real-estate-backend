from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class BookingCreate(BaseModel):

    check_in: datetime
    check_out: datetime


class BookingUpdate(BaseModel):

    status: str


class BookingResponse(BaseModel):

    id: int
    user_id: int
    property_id: int

    check_in: datetime
    check_out: datetime

    total_price: int
    status: str

    class Config:
        from_attributes = True