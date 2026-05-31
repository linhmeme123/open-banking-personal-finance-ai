from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class AccountOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    account_name: str
    account_type: str
    currency: str
    balance: Decimal
    provider_code: str
    provider_name: str
    provider_type: str
