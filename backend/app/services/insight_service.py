from decimal import Decimal
from sqlalchemy.orm import Session

from app.models.domain import Transaction


def get_monthly_summary(db: Session, user_id: int):
    transactions = (
        db.query(Transaction)
        .join(Transaction.account)
        .filter(Transaction.account.has(user_id=user_id))
        .all()
    )

    income = sum(t.amount for t in transactions if t.direction == "income") or Decimal("0")
    expense = sum(abs(t.amount) for t in transactions if t.direction == "expense") or Decimal("0")

    category_breakdown: dict[str, Decimal] = {}
    for tx in transactions:
        if tx.direction == "expense":
            category = tx.category or "uncategorized"
            category_breakdown[category] = category_breakdown.get(category, Decimal("0")) + abs(tx.amount)

    return {
        "income": float(income),
        "expense": float(expense),
        "net_cashflow": float(income - expense),
        "category_breakdown": [
            {"category": category, "amount": float(amount)}
            for category, amount in category_breakdown.items()
        ],
    }
