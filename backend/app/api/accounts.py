from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.domain import Account

router = APIRouter()


@router.get("")
def list_accounts(db: Session = Depends(get_db)):
    accounts = db.query(Account).all()
    return [
        {
            "id": account.id,
            "account_name": account.account_name,
            "account_type": account.account_type,
            "currency": account.currency,
            "balance": float(account.balance),
            "provider_name": account.provider.name,
        }
        for account in accounts
    ]
