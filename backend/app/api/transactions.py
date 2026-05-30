from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.user import User

router = APIRouter()


@router.get("")
def list_transactions(
    month: str | None = Query(default=None),
    category: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = (
        db.query(Transaction)
        .join(Account)
        .filter(Account.user_id == current_user.id)
        .order_by(Transaction.transaction_time.desc())
    )
    if month:
        query = query.filter(Transaction.transaction_time >= f"{month}-01")
        if month.endswith("-12"):
            next_month = f"{int(month[:4]) + 1}-01"
        else:
            next_month = f"{month[:5]}{int(month[5:]) + 1:02d}"
        query = query.filter(Transaction.transaction_time < f"{next_month}-01")
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
