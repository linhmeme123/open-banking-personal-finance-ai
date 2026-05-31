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


class BankProviderClient(ABC):
    def __init__(self, db: Session, provider_code: str):
        self.db = db
        self.provider_code = provider_code

    @abstractmethod
    def connect(self, user: User, provider: BankProvider, scope: str) -> ProviderConnectionResult:
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
