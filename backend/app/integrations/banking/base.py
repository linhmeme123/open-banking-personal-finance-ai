from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.bank import BankConnection, BankProvider
from app.models.user import User


@dataclass
class ProviderAccount:
    external_account_id: str
    account_name: str
    account_type: str
    currency: str
    balance: Decimal


@dataclass
class ProviderTransaction:
    external_transaction_id: str
    external_account_id: str
    transaction_time: datetime
    description: str
    merchant_name: str | None
    amount: Decimal
    currency: str
    direction: str


@dataclass
class ProviderConnectionResult:
    provider_code: str
    status: str
    access_token: str | None = None
    refresh_token: str | None = None
    expires_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ProviderAuthorization:
    provider_code: str
    required_fields: list[str]
    available_scopes: list[str]
    available_accounts: list[dict[str, Any]]


class BankProviderClient(ABC):
    def __init__(self, db: Session, provider_code: str):
        self.db = db
        self.provider_code = provider_code

    @abstractmethod
    def connect(self, user: User, provider: BankProvider, scope: str) -> ProviderConnectionResult:
        raise NotImplementedError

    @abstractmethod
    def initiate_authorization(self, user: User, provider: BankProvider) -> ProviderAuthorization:
        raise NotImplementedError

    @abstractmethod
    def authorize(
        self,
        user: User,
        provider: BankProvider,
        credentials: dict[str, str | None],
        scope: str,
        selected_account_ids: list[str],
    ) -> ProviderConnectionResult:
        raise NotImplementedError

    @abstractmethod
    def get_accounts(self, connection: BankConnection) -> list[ProviderAccount]:
        raise NotImplementedError

    @abstractmethod
    def get_transactions(
        self,
        connection: BankConnection,
        account: Account,
        since: datetime | None = None,
    ) -> list[ProviderTransaction]:
        raise NotImplementedError

    @abstractmethod
    def verify_webhook(self, payload: dict[str, Any], headers: dict[str, str]) -> bool:
        raise NotImplementedError

    @abstractmethod
    def normalize_account(self, raw_account: dict[str, Any]) -> ProviderAccount:
        raise NotImplementedError

    @abstractmethod
    def normalize_transaction(self, raw_transaction: dict[str, Any]) -> ProviderTransaction:
        raise NotImplementedError

    def list_mock_accounts(self) -> list[dict[str, Any]]:
        raise NotImplementedError("This provider does not expose a mock bank console")

    def create_mock_account(self, **values: Any) -> dict[str, Any]:
        raise NotImplementedError("This provider does not expose a mock bank console")

    def list_mock_transactions(self, external_account_id: str | None = None) -> list[dict[str, Any]]:
        raise NotImplementedError("This provider does not expose a mock bank console")

    def create_mock_transaction(self, **values: Any) -> dict[str, Any]:
        raise NotImplementedError("This provider does not expose a mock bank console")

    def generate_mock_transaction(self, external_account_id: str) -> dict[str, Any]:
        raise NotImplementedError("This provider does not expose a mock bank console")

    def get_mock_transaction(self, external_transaction_id: str) -> dict[str, Any] | None:
        raise NotImplementedError("This provider does not expose a mock bank console")

    def list_mock_transaction_events(self, external_transaction_id: str) -> list[dict[str, Any]]:
        raise NotImplementedError("This provider does not expose a mock bank console")

    def record_webhook_sent(self, external_transaction_id: str) -> None:
        pass

    def get_webhook_headers(self) -> dict[str, str]:
        return {}

    def record_webhook_verified(self, external_transaction_id: str) -> None:
        pass

    def record_transaction_synced(
        self,
        external_transaction_id: str,
        *,
        category: str | None = None,
    ) -> None:
        pass

    def record_balance_updated(
        self,
        external_transaction_id: str,
        *,
        balance_before: Decimal,
        balance_after: Decimal,
        currency: str,
    ) -> None:
        pass

    def record_transaction_failed(self, external_transaction_id: str, reason: str) -> None:
        pass
