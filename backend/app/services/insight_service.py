from decimal import Decimal
from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.budget import Budget
from app.models.transaction import Transaction


def get_user_transactions(db: Session, user_id: int, month: str | None = None):
    query = (
        db.query(Transaction)
        .join(Account)
        .filter(Account.user_id == user_id)
    )
    if month:
        year = int(month[:4])
        month_number = int(month[5:])
        if month_number == 12:
            next_month = f"{year + 1}-01"
        else:
            next_month = f"{year}-{month_number + 1:02d}"
        query = query.filter(Transaction.transaction_time >= f"{month}-01")
        query = query.filter(Transaction.transaction_time < f"{next_month}-01")
    return query.all()


def get_category_breakdown(db: Session, user_id: int, month: str | None = None):
    transactions = get_user_transactions(db, user_id, month)

    category_breakdown: dict[str, Decimal] = {}
    for tx in transactions:
        if tx.direction == "expense":
            category = tx.category or "uncategorized"
            category_breakdown[category] = category_breakdown.get(category, Decimal("0")) + abs(tx.amount)

    return [
        {"category": category, "amount": float(amount)}
        for category, amount in sorted(category_breakdown.items(), key=lambda item: item[1], reverse=True)
    ]


def get_recurring_payments(db: Session, user_id: int):
    transactions = get_user_transactions(db, user_id)
    grouped: dict[tuple[str, Decimal], list[Transaction]] = {}
    for tx in transactions:
        if tx.direction != "expense":
            continue
        key = (tx.merchant_name or tx.description, abs(tx.amount))
        grouped.setdefault(key, []).append(tx)

    recurring = []
    for (merchant, amount), items in grouped.items():
        if len(items) < 2:
            continue
        latest = max(item.transaction_time for item in items)
        recurring.append(
            {
                "merchant_name": merchant,
                "amount": float(amount),
                "currency": items[0].currency,
                "occurrences": len(items),
                "latest_transaction_time": latest.isoformat(),
            }
        )
    return recurring


def get_budget_status(db: Session, user_id: int, month: str | None = None):
    budgets = db.query(Budget).filter(Budget.user_id == user_id).all()
    spending = {item["category"]: Decimal(str(item["amount"])) for item in get_category_breakdown(db, user_id, month)}

    return [
        {
            "category": budget.category,
            "month": budget.month,
            "monthly_limit": float(budget.monthly_limit),
            "spent": float(spending.get(budget.category, Decimal("0"))),
            "remaining": float(budget.monthly_limit - spending.get(budget.category, Decimal("0"))),
        }
        for budget in budgets
    ]


def get_monthly_summary(db: Session, user_id: int, month: str | None = None):
    transactions = (
        get_user_transactions(db, user_id, month)
    )

    income = sum(t.amount for t in transactions if t.direction == "income") or Decimal("0")
    expense = sum(abs(t.amount) for t in transactions if t.direction == "expense") or Decimal("0")

    return {
        "income": float(income),
        "expense": float(expense),
        "net_cashflow": float(income - expense),
        "category_breakdown": get_category_breakdown(db, user_id, month),
        "budget_status": get_budget_status(db, user_id, month),
    }
