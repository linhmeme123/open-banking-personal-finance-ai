from typing import Any

from app.integrations.banking import fake_bank_store
from app.integrations.banking.base import (
    BankProviderClient,
    ProviderAccount,
    ProviderConnectionResult,
    ProviderTransaction,
)
from app.models.account import Account
from app.models.bank import BankConnection, BankProvider
from app.models.user import User


class FakeBankClient(BankProviderClient):
    def connect(self, user: User, provider: BankProvider, scope: str) -> ProviderConnectionResult:
        fake_bank_store.list_accounts(provider.code)
        return ProviderConnectionResult(provider_code=provider.code, status="connected")

    def get_accounts(self, connection: BankConnection) -> list[ProviderAccount]:
        return [self.normalize_account(item) for item in fake_bank_store.list_accounts(self.provider_code)]

    def get_transactions(self, connection: BankConnection, account: Account, since=None) -> list[ProviderTransaction]:
        items = fake_bank_store.list_transactions(self.provider_code, account.external_account_id)
        return [self.normalize_transaction(item) for item in items if not since or item["transaction_time"] > since]

    def verify_webhook(self, payload: dict[str, Any], headers: dict[str, str]) -> bool:
        return headers.get("x-fake-bank-signature") == "velora-fake-bank"

    def normalize_account(self, raw_account: dict[str, Any]) -> ProviderAccount:
        return ProviderAccount(**raw_account)

    def normalize_transaction(self, raw_transaction: dict[str, Any]) -> ProviderTransaction:
        return ProviderTransaction(**raw_transaction)
