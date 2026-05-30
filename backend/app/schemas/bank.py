from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProviderConnectRequest(BaseModel):
    provider_code: str
    scope: str = "accounts:read transactions:read"


class SyncRequest(BaseModel):
    provider_code: str = "BANK_A"


class BankConnectionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    provider_code: str
    provider_name: str
    status: str
    consent_scope: str
    last_synced_at: datetime | None