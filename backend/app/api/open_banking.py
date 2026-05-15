from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.domain import Account, BankProvider, Transaction, User
from app.services.open_banking_mock import get_mock_providers, get_mock_transactions
from app.ai.categorizer import categorize_transaction

router = APIRouter()


@router.get("/providers")
def providers():
    return get_mock_providers()


@router.post("/sync")
def sync_open_banking_data(db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == "demo@pfai.local").first()
    if not user:
        user = User(full_name="Demo User", email="demo@pfai.local")
        db.add(user)
        db.commit()
        db.refresh(user)

    provider = db.query(BankProvider).filter(BankProvider.code == "BANK_A").first()
    if not provider:
        provider = BankProvider(code="BANK_A", name="Bank A Sandbox")
        db.add(provider)
        db.commit()
        db.refresh(provider)

    account = db.query(Account).filter(Account.user_id == user.id).first()
    if not account:
        account = Account(
            user_id=user.id,
            provider_id=provider.id,
            account_name="Main Checking Account",
            account_type="checking",
            currency="VND",
            balance=15000000,
        )
        db.add(account)
        db.commit()
        db.refresh(account)

    created = 0
    for item in get_mock_transactions(account.id):
        existing = db.query(Transaction).filter(Transaction.external_id == item["external_id"]).first()
        if existing:
            continue

        category, confidence = categorize_transaction(item["description"], item.get("merchant_name"))
        tx = Transaction(**item, category=category, category_confidence=confidence)
        db.add(tx)
        created += 1

    db.commit()
    return {"status": "synced", "created_transactions": created}
