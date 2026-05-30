from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ConsentCreate(BaseModel):
    provider_code: str
    scope: str
    action: str


class ConsentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    provider_code: str
    scope: str
    action: str
    event_hash: str
    created_at: datetime