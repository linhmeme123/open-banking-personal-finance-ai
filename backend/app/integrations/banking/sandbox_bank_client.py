from typing import Any

from app.integrations.banking.base import (
    BankProviderClient,
    ProviderAccount,
    ProviderConnectionResult,
    ProviderTransaction,
)
from app.models.account import Account
from app.models.bank import BankConnection, BankProvider
from app.models.user import User


class SandboxBankClient(BankProviderClient):
    """Adapter placeholder for a public sandbox API integration."""

    def connect(self, user: User, provider: BankProvider, scope: str) -> ProviderConnectionResult:
        return ProviderConnectionResult(provider_code=provider.code, status="connected")

    def get_accounts(self, connection: BankConnection) -> list[ProviderAccount]:
        return []

    def get_transactions(self, connection: BankConnection, account: Account, since=None) -> list[ProviderTransaction]:
        return []

    def verify_webhook(self, payload: dict[str, Any], headers: dict[str, str]) -> bool:
        return bool(headers.get("x-sandbox-signature"))

    def normalize_account(self, raw_account: dict[str, Any]) -> ProviderAccount:
        return ProviderAccount(**raw_account)

    def normalize_transaction(self, raw_transaction: dict[str, Any]) -> ProviderTransaction:
        return ProviderTransaction(**raw_transaction)
