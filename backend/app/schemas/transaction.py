from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class TransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    transaction_time: datetime
    description: str
    merchant_name: str | None
    amount: Decimal
    currency: str
    direction: str
    category: str | None
    category_confidence: Decimal | None


class CategorizeRequest(BaseModel):
    transaction_id: int


class CategorizeResponse(BaseModel):
    transaction_id: int
    category: str
    confidence: float