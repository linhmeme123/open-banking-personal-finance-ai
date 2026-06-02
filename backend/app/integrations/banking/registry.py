from dataclasses import dataclass

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.integrations.banking.base import BankProviderClient
from app.integrations.banking.fake_bank_client import FakeBankClient
from app.integrations.banking.real_bank_client import RealBankClient
from app.integrations.banking.sandbox_bank_client import SandboxBankClient


DEFAULT_SCOPES = ["accounts:read", "balances:read", "transactions:read"]


@dataclass(frozen=True)
class ProviderDefinition:
    code: str
    name: str
    type: str
    client_class: type[BankProviderClient]
    logo_url: str | None = None
    status: str = "available"
    supported_scopes: tuple[str, ...] = tuple(DEFAULT_SCOPES)
    mock_console: bool = False

    def serialize(self) -> dict:
        return {
            "code": self.code,
            "name": self.name,
            "type": self.type,
            "logo_url": self.logo_url,
            "status": self.status,
            "supported_scopes": list(self.supported_scopes),
        }


PROVIDERS = (
    ProviderDefinition("VPBANK_MOCK", "VPBank Mock", "mock_bank", FakeBankClient, mock_console=True),
    ProviderDefinition("TECHCOMBANK_MOCK", "Techcombank Mock", "mock_bank", FakeBankClient, mock_console=True),
    ProviderDefinition("MOMO_MOCK", "MoMo Mock", "mock_bank", FakeBankClient, mock_console=True),
    ProviderDefinition("OPEN_BANK_PROJECT_SANDBOX", "Open Bank Project Sandbox", "sandbox", SandboxBankClient),
    ProviderDefinition("REAL_BANK_PARTNER", "Real Bank Partner", "real_partner", RealBankClient, status="coming_soon"),
)


def list_provider_definitions() -> list[ProviderDefinition]:
    return list(PROVIDERS)


def normalize_provider_code(provider_code: str) -> str:
    return provider_code.strip().upper()


def get_provider_definition(provider_code: str) -> ProviderDefinition:
    normalized_code = normalize_provider_code(provider_code)
    provider = next((item for item in PROVIDERS if item.code == normalized_code), None)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider


def get_provider_client(db: Session, provider_code: str) -> BankProviderClient:
    provider = get_provider_definition(provider_code)
    return provider.client_class(db, provider.code)
