from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProviderConnectRequest(BaseModel):
    provider_code: str


class ProviderAuthorizeRequest(BaseModel):
    provider_code: str
    username: str | None = None
    customer_id: str | None = None
    account_number: str | None = None
    otp_code: str | None = None
    scopes: list[str]
    selected_account_ids: list[str] = Field(default_factory=list)


class SyncRequest(BaseModel):
    provider_code: str = "VPBANK_MOCK"


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
    selected_account_ids: list[str]
    last_synced_at: datetime | None
