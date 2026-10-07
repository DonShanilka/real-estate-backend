from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MessageCreate(BaseModel):

    receiver_id: int
    property_id: Optional[int] = None
    message: str


class MessageResponse(BaseModel):

    id: int

    sender_id: int
    receiver_id: int

    property_id: Optional[int]

    message: str

    is_read: bool

    created_at: datetime

    class Config:
        from_attributes = True