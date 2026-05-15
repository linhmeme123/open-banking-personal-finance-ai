from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.domain import Transaction

router = APIRouter()


@router.get("")
def list_transactions(
    category: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(Transaction).order_by(Transaction.transaction_time.desc())
    if category:
        query = query.filter(Transaction.category == category)

    transactions = query.all()
    return [
        {
            "id": tx.id,
            "transaction_time": tx.transaction_time.isoformat(),
            "description": tx.description,
            "merchant_name": tx.merchant_name,
            "amount": float(tx.amount),
            "currency": tx.currency,
            "direction": tx.direction,
            "category": tx.category,
            "category_confidence": float(tx.category_confidence) if tx.category_confidence else None,
        }
        for tx in transactions
    ]
