from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel


class AccountOut(BaseModel):
    id: int
    account_name: str
    account_type: str
    currency: str
    balance: Decimal
    provider_name: str

    class Config:
        from_attributes = True


class TransactionOut(BaseModel):
    id: int
    transaction_time: datetime
    description: str
    merchant_name: str | None
    amount: Decimal
    currency: str
    direction: str
    category: str | None
    category_confidence: Decimal | None

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    user_id: int = 1
    message: str


class ChatResponse(BaseModel):
    answer: str


class CategorizeRequest(BaseModel):
    transaction_id: int


class CategorizeResponse(BaseModel):
    transaction_id: int
    category: str
    confidence: float


class ConsentCreate(BaseModel):
    user_id: int = 1
    provider_code: str
    scope: str
    action: str


class ConsentOut(BaseModel):
    id: int
    provider_code: str
    scope: str
    action: str
    event_hash: str
    created_at: datetime

    class Config:
        from_attributes = True
