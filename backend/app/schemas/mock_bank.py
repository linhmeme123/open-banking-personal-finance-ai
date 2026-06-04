from datetime import datetime
from decimal import Decimal

from typing import Literal

from pydantic import BaseModel, Field


class MockBankAccountCreate(BaseModel):
    provider_code: str
    account_name: str
    account_type: str = "checking"
    currency: str = "VND"
    balance: Decimal = Decimal("0")


class MockBankTransactionCreate(BaseModel):
    provider_code: str
    external_account_id: str
    description: str
    merchant_name: str | None = None
    amount: Decimal
    direction: Literal["income", "expense"]
    category: str | None = None
    transaction_time: datetime | None = None


class MockBankMovementRequest(BaseModel):
    provider_code: str
    external_account_id: str
    amount: Decimal = Field(gt=0)


class MockBankTransferRequest(BaseModel):
    provider_code: str
    external_account_id: str
    recipient_bank_name: str = Field(min_length=1)
    recipient_account_number: str = Field(min_length=1)
    recipient_account_name: str = Field(min_length=1)
    amount: Decimal = Field(gt=0)
    note: str | None = None


class MockBankWebhookSendRequest(BaseModel):
    provider_code: str
    external_transaction_id: str


class BankWebhookPayload(BaseModel):
    provider_code: str
    transaction: dict
