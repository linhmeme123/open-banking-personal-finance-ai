from typing import Any

from app.integrations.banking.base import (
    BankProviderClient,
    ProviderAccount,
    ProviderAuthorization,
    ProviderConnectionResult,
    ProviderTransaction,
)
from app.models.account import Account
from app.models.bank import BankConnection, BankProvider
from app.models.user import User


class SandboxBankClient(BankProviderClient):
    """Adapter placeholder for a public sandbox API integration."""

    def connect(self, user: User, provider: BankProvider, scope: str) -> ProviderConnectionResult:
        raise NotImplementedError("Use the authorization flow to connect this provider")

    def initiate_authorization(self, user: User, provider: BankProvider) -> ProviderAuthorization:
        return ProviderAuthorization(
            provider_code=provider.code,
            required_fields=["username", "otp_code"],
            available_scopes=list(provider.supported_scopes),
            available_accounts=[],
        )

    def authorize(
        self,
        user: User,
        provider: BankProvider,
        credentials: dict[str, str | None],
        scope: str,
        selected_account_ids: list[str],
    ) -> ProviderConnectionResult:
        if not (credentials.get("username") or credentials.get("customer_id")):
            raise ValueError("Enter a sandbox username or customer ID")
        if credentials.get("otp_code") != "123456":
            raise ValueError("Invalid OTP code. Use 123456 for this sandbox demo.")
        return ProviderConnectionResult(provider_code=provider.code, status="authorized")

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
