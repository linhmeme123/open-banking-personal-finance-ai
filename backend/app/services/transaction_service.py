from datetime import date, datetime, time, timedelta
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.ai.categorizer import categorize_transaction
from app.models.account import Account
from app.models.bank import BankProvider
from app.models.transaction import Transaction


def serialize_transaction(transaction: Transaction):
    return {
        "id": transaction.id,
        "transaction_time": transaction.transaction_time.isoformat(),
        "description": transaction.description,
        "merchant_name": transaction.merchant_name,
        "amount": float(transaction.amount),
        "currency": transaction.currency,
        "direction": transaction.direction,
        "category": transaction.category,
        "category_confidence": (
            float(transaction.category_confidence)
            if transaction.category_confidence is not None
            else None
        ),
        "account_name": transaction.account.account_name,
        "provider_code": transaction.account.provider.code,
        "provider_name": transaction.account.provider.name,
        "provider_type": transaction.account.provider.provider_type,
    }


def query_user_transactions(
    db: Session,
    user_id: int,
    *,
    month: str | None = None,
    provider_code: str | None = None,
    category: str | None = None,
    direction: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    min_amount: Decimal | None = None,
    max_amount: Decimal | None = None,
    search: str | None = None,
):
    query = (
        db.query(Transaction)
        .join(Account)
        .join(BankProvider)
        .filter(Account.user_id == user_id)
    )
    if month:
        try:
            month_start = datetime.strptime(month, "%Y-%m")
        except ValueError as exc:
            raise HTTPException(status_code=422, detail="month must use YYYY-MM format") from exc
        next_month = (
            month_start.replace(year=month_start.year + 1, month=1)
            if month_start.month == 12
            else month_start.replace(month=month_start.month + 1)
        )
        query = query.filter(Transaction.transaction_time >= month_start)
        query = query.filter(Transaction.transaction_time < next_month)
    if provider_code:
        query = query.filter(BankProvider.code == provider_code)
    if category:
        query = query.filter(Transaction.category == category)
    if direction:
        query = query.filter(Transaction.direction == direction)
    if date_from:
        query = query.filter(Transaction.transaction_time >= datetime.combine(date_from, time.min))
    if date_to:
        query = query.filter(
            Transaction.transaction_time < datetime.combine(date_to + timedelta(days=1), time.min)
        )
    if min_amount is not None:
        query = query.filter(func.abs(Transaction.amount) >= min_amount)
    if max_amount is not None:
        query = query.filter(func.abs(Transaction.amount) <= max_amount)
    if search:
        pattern = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Transaction.description.ilike(pattern),
                func.coalesce(Transaction.merchant_name, "").ilike(pattern),
            )
        )
    return query.order_by(Transaction.transaction_time.desc())


def categorize_user_transaction(db: Session, user_id: int, transaction_id: int):
    transaction = (
        db.query(Transaction)
        .join(Account)
        .filter(Transaction.id == transaction_id, Account.user_id == user_id)
        .first()
    )
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    category, confidence = categorize_transaction(transaction.description, transaction.merchant_name)
    transaction.category = category
    transaction.category_confidence = confidence
    db.commit()
    return {"transaction_id": transaction.id, "category": category, "confidence": confidence}


def categorize_uncategorized_transactions(db: Session, user_id: int, provider_code: str | None = None):
    query = query_user_transactions(db, user_id, provider_code=provider_code).filter(Transaction.category.is_(None))
    results = []
    for transaction in query.all():
        category, confidence = categorize_transaction(transaction.description, transaction.merchant_name)
        transaction.category = category
        transaction.category_confidence = confidence
        results.append({"transaction_id": transaction.id, "category": category, "confidence": confidence})
    db.commit()
    return {"categorized_count": len(results), "transactions": results}
