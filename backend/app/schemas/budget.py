from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class BudgetCreate(BaseModel):
    category: str
    month: str
    monthly_limit: Decimal


class BudgetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category: str
    month: str
    monthly_limit: Decimal