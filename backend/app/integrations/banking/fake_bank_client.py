from datetime import datetime
from decimal import Decimal
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
        return ProviderAccount(
            external_account_id=raw_account["external_account_id"],
            account_name=raw_account["account_name"],
            account_type=raw_account["account_type"],
            currency=raw_account["currency"],
            balance=raw_account["balance"],
        )

    def normalize_transaction(self, raw_transaction: dict[str, Any]) -> ProviderTransaction:
        transaction_time = raw_transaction["transaction_time"]
        if isinstance(transaction_time, str):
            transaction_time = datetime.fromisoformat(transaction_time.replace("Z", "+00:00"))
        return ProviderTransaction(
            external_transaction_id=raw_transaction["external_transaction_id"],
            external_account_id=raw_transaction["external_account_id"],
            transaction_time=transaction_time,
            description=raw_transaction["description"],
            merchant_name=raw_transaction.get("merchant_name"),
            amount=Decimal(str(raw_transaction["amount"])),
            currency=raw_transaction["currency"],
            direction=raw_transaction["direction"],
        )

    def list_mock_accounts(self) -> list[dict[str, Any]]:
        return fake_bank_store.list_accounts(self.provider_code)

    def create_mock_account(self, **values: Any) -> dict[str, Any]:
        return fake_bank_store.create_account(self.provider_code, **values)

    def list_mock_transactions(self, external_account_id: str | None = None) -> list[dict[str, Any]]:
        return fake_bank_store.list_transactions(self.provider_code, external_account_id)

    def create_mock_transaction(self, **values: Any) -> dict[str, Any]:
        return fake_bank_store.create_transaction(self.provider_code, **values)

    def generate_mock_transaction(self, external_account_id: str) -> dict[str, Any]:
        return fake_bank_store.generate_transaction(self.provider_code, external_account_id)

    def get_mock_transaction(self, external_transaction_id: str) -> dict[str, Any] | None:
        return fake_bank_store.get_transaction(self.provider_code, external_transaction_id)

    def list_mock_transaction_events(self, external_transaction_id: str) -> list[dict[str, Any]]:
        return fake_bank_store.list_transaction_events(self.provider_code, external_transaction_id)

    def record_webhook_sent(self, external_transaction_id: str) -> None:
        fake_bank_store.mark_webhook_sent(self.provider_code, external_transaction_id)

    def get_webhook_headers(self) -> dict[str, str]:
        return {"x-fake-bank-signature": "velora-fake-bank"}

    def record_webhook_verified(self, external_transaction_id: str) -> None:
        fake_bank_store.mark_webhook_verified(self.provider_code, external_transaction_id)

    def record_transaction_synced(self, external_transaction_id: str, *, category: str | None = None) -> None:
        fake_bank_store.mark_transaction_synced(self.provider_code, external_transaction_id, category)

    def record_balance_updated(
        self,
        external_transaction_id: str,
        *,
        balance_before: Decimal,
        balance_after: Decimal,
        currency: str,
    ) -> None:
        fake_bank_store.record_balance_updated(
            self.provider_code,
            external_transaction_id,
            balance_before,
            balance_after,
            currency,
        )

    def record_transaction_failed(self, external_transaction_id: str, reason: str) -> None:
        fake_bank_store.mark_transaction_failed(self.provider_code, external_transaction_id, reason)
