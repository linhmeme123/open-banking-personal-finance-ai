from datetime import datetime
from decimal import Decimal

from typing import Literal

from pydantic import BaseModel


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


class MockBankGenerateRequest(BaseModel):
    provider_code: str
    external_account_id: str


class MockBankWebhookSendRequest(BaseModel):
    provider_code: str
    external_transaction_id: str


class BankWebhookPayload(BaseModel):
    provider_code: str
    transaction: dict
