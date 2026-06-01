from collections import defaultdict
from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.integrations.ai.registry import get_ai_provider
from app.models.account import Account
from app.models.bank import BankConnection, BankProvider
from app.models.budget import Budget
from app.models.chat_message import AiChatMessage
from app.models.transaction import Transaction
from app.models.user import User


MAX_RECENT_TRANSACTIONS = 20
MAX_TRANSACTIONS_FOR_RECURRING = 100
MAX_CHAT_HISTORY_MESSAGES = 6


def _as_float(value: Decimal) -> float:
    return float(value)


def _truncate(value: str | None, limit: int = 80) -> str:
    return (value or "")[:limit]


def _summarize_recurring_merchants(transactions: list[Transaction]) -> list[dict]:
    grouped: dict[tuple[str, str], list[Transaction]] = defaultdict(list)
    for transaction in transactions:
        if transaction.direction != "expense":
            continue
        merchant = transaction.merchant_name or transaction.description
        grouped[(_truncate(merchant), transaction.currency)].append(transaction)

    recurring = []
    for (merchant, currency), items in grouped.items():
        if len(items) < 2:
            continue
        amounts = [abs(item.amount) for item in items]
        recurring.append(
            {
                "merchant": merchant,
                "currency": currency,
                "occurrences": len(items),
                "average_amount": _as_float(sum(amounts) / len(amounts)),
            }
        )
    return sorted(recurring, key=lambda item: item["occurrences"], reverse=True)[:5]


def build_financial_context(db: Session, user: User) -> dict:
    if not user or not user.id:
        raise ValueError("Authenticated user is required")

    now = datetime.utcnow()
    month = now.strftime("%Y-%m")
    month_start = datetime(now.year, now.month, 1)

    accounts = db.query(Account).filter(Account.user_id == user.id).all()
    monthly_transactions = (
        db.query(Transaction)
        .join(Account)
        .filter(Account.user_id == user.id)
        .filter(Transaction.transaction_time >= month_start)
        .order_by(Transaction.transaction_time.desc())
        .all()
    )
    recent_transactions = (
        db.query(Transaction)
        .join(Account)
        .filter(Account.user_id == user.id)
        .order_by(Transaction.transaction_time.desc())
        .limit(MAX_TRANSACTIONS_FOR_RECURRING)
        .all()
    )
    budgets = (
        db.query(Budget)
        .filter(Budget.user_id == user.id)
        .filter(Budget.month == month)
        .order_by(Budget.category.asc())
        .limit(20)
        .all()
    )
    connected_providers = (
        db.query(BankProvider.code)
        .join(BankConnection)
        .filter(BankConnection.user_id == user.id)
        .filter(BankConnection.status == "connected")
        .order_by(BankProvider.code.asc())
        .all()
    )

    balances: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    for account in accounts:
        balances[account.currency] += account.balance

    income: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    expense: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    category_spending: dict[tuple[str, str], Decimal] = defaultdict(lambda: Decimal("0"))
    for transaction in monthly_transactions:
        if transaction.direction == "income":
            income[transaction.currency] += transaction.amount
        elif transaction.direction == "expense":
            amount = abs(transaction.amount)
            expense[transaction.currency] += amount
            category_spending[(transaction.category or "uncategorized", transaction.currency)] += amount

    top_categories = [
        {"category": category, "currency": currency, "amount": _as_float(amount)}
        for (category, currency), amount in sorted(
            category_spending.items(),
            key=lambda item: item[1],
            reverse=True,
        )[:5]
    ]
    spent_by_category = {
        category: sum(
            amount
            for (spent_category, _currency), amount in category_spending.items()
            if spent_category == category
        )
        for category in {budget.category for budget in budgets}
    }

    return {
        "synced_data_available": bool(accounts or recent_transactions),
        "summary_month": month,
        "account_count": len(accounts),
        "connected_providers": [provider.code for provider in connected_providers],
        "total_balance": {currency: _as_float(amount) for currency, amount in balances.items()},
        "monthly_income": {currency: _as_float(amount) for currency, amount in income.items()},
        "monthly_expense": {currency: _as_float(amount) for currency, amount in expense.items()},
        "top_categories": top_categories,
        "budgets": [
            {
                "category": budget.category,
                "month": budget.month,
                "monthly_limit": _as_float(budget.monthly_limit),
                "spent": _as_float(spent_by_category.get(budget.category, Decimal("0"))),
            }
            for budget in budgets
        ],
        "recent_transactions": [
            {
                "date": transaction.transaction_time.date().isoformat(),
                "description": _truncate(transaction.description),
                "merchant": _truncate(transaction.merchant_name),
                "amount": _as_float(abs(transaction.amount)),
                "currency": transaction.currency,
                "direction": transaction.direction,
                "category": transaction.category or "uncategorized",
            }
            for transaction in recent_transactions[:MAX_RECENT_TRANSACTIONS]
        ],
        "recurring_merchants": _summarize_recurring_merchants(recent_transactions),
    }


def _load_recent_chat_history(db: Session, user_id: int) -> list[dict[str, str]]:
    messages = (
        db.query(AiChatMessage)
        .filter(AiChatMessage.user_id == user_id)
        .order_by(AiChatMessage.created_at.desc(), AiChatMessage.id.desc())
        .limit(MAX_CHAT_HISTORY_MESSAGES)
        .all()
    )
    return [
        {"role": message.role, "content": _truncate(message.content, 500)}
        for message in reversed(messages)
        if message.role in {"user", "assistant"}
    ]


def answer_personal_finance_question(db: Session, user: User, message: str) -> dict:
    provider = get_ai_provider()
    context = build_financial_context(db, user)
    answer = provider.generate_answer(
        message=message,
        financial_context=context,
        chat_history=_load_recent_chat_history(db, user.id),
    )
    db.add(AiChatMessage(user_id=user.id, role="user", content=message))
    db.add(AiChatMessage(user_id=user.id, role="assistant", content=answer))
    db.commit()
    return {
        "answer": answer,
        "provider": provider.provider_name,
        "context_used": context["synced_data_available"],
    }
