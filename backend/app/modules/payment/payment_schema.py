from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


PaymentMethod = Literal[
    "card",
    "bank_transfer",
    "cash",
]

PaymentStatus = Literal[
    "pending",
    "successful",
    "failed",
    "refunded",
]


class PaymentCreate(BaseModel):
    
    user_id: int = Field(gt=0)
    booking_id: int = Field(gt=0)
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    currency: str = Field(default="LKR", min_length=3, max_length=3)
    payment_method: PaymentMethod
    status: PaymentStatus = "pending"
    transaction_id: str | None = Field(
        default=None,
        max_length=255,
    )

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, value: str) -> str:
        return value.upper()


class PaymentUpdate(BaseModel):
    amount: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=12,
        decimal_places=2,
    )

    currency: str | None = Field(
        default=None,
        min_length=3,
        max_length=3,
    )

    payment_method: PaymentMethod | None = None
    status: PaymentStatus | None = None
    transaction_id: str | None = Field(
        default=None,
        max_length=255,
    )

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, value: str | None) -> str | None:
        return value.upper() if value else value


class PaymentResponse(BaseModel):
    id: int
    user_id: int
    booking_id: int
    amount: Decimal
    currency: str
    payment_method: str
    status: str
    transaction_id: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)