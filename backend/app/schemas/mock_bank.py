from datetime import datetime
from decimal import Decimal

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
    direction: str


class MockBankGenerateRequest(BaseModel):
    provider_code: str
    external_account_id: str


class MockBankWebhookSendRequest(BaseModel):
    provider_code: str
    external_transaction_id: str


class BankWebhookPayload(BaseModel):
    provider_code: str
    transaction: dict
