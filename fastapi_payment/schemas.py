from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict

class PaymentRequest(BaseModel):
    card_id: int = Field(..., description="ID of the user's saved card to charge")
    amount: Decimal = Field(..., gt=0, decimal_places=2, description="Payment amount (must be positive)")
    currency: str = Field(default="USD", max_length=10, description="Payment currency (e.g. USD, EUR, INR)")
    cvv: str = Field(..., min_length=3, max_length=4, description="Card Verification Value (used for validation, never stored)")
    description: Optional[str] = Field(default="Card Payment", max_length=255, description="Payment purpose or description")

    @field_validator('cvv')
    @classmethod
    def validate_cvv(cls, v: str) -> str:
        clean = v.strip()
        if not (clean.isdigit() and len(clean) in (3, 4)):
            raise ValueError("CVV must be 3 or 4 digits")
        return clean


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    transaction_id: str
    user_id: int
    card_id: int
    amount: Decimal
    currency: str
    status: str  # PENDING, SUCCESS, FAILED
    description: str
    failure_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class TransactionStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    transaction_id: str
    status: str
    amount: Decimal
    currency: str
    failure_reason: Optional[str] = None
    created_at: datetime
