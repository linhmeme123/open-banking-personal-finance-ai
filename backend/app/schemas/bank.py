from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProviderConnectRequest(BaseModel):
    provider_code: str
    scope: str = "accounts:read transactions:read balance:read"


class SyncRequest(BaseModel):
    provider_code: str = "TIMO"


class ProviderOut(BaseModel):
    code: str
    name: str
    type: str
    logo_url: str | None
    status: str
    supported_scopes: list[str]


class BankConnectionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    provider_code: str
    provider_name: str
    provider_type: str
    logo_url: str | None
    status: str
    consent_scope: str
    last_synced_at: datetime | None
