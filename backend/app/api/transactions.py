from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.transaction import CategorizeAllRequest, CategorizeRequest
from app.services.transaction_service import (
    categorize_uncategorized_transactions,
    categorize_user_transaction,
    query_user_transactions,
    serialize_transaction,
)

router = APIRouter()


@router.get("")
def list_transactions(
    month: str | None = Query(default=None),
    provider_code: str | None = Query(default=None),
    category: str | None = Query(default=None),
    direction: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    min_amount: Decimal | None = Query(default=None, ge=0),
    max_amount: Decimal | None = Query(default=None, ge=0),
    search: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transactions = query_user_transactions(
        db,
        current_user.id,
        month=month,
        provider_code=provider_code,
        category=category,
        direction=direction,
        date_from=date_from,
        date_to=date_to,
        min_amount=min_amount,
        max_amount=max_amount,
        search=search,
    ).all()
    return [serialize_transaction(transaction) for transaction in transactions]


@router.post("/categorize")
def categorize(
    payload: CategorizeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return categorize_user_transaction(db, current_user.id, payload.transaction_id)


@router.post("/categorize-all")
def categorize_all(
    payload: CategorizeAllRequest | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return categorize_uncategorized_transactions(
        db,
        current_user.id,
        payload.provider_code if payload else None,
    )
