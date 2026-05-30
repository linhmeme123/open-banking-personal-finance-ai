from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.account import Account
from app.models.user import User

router = APIRouter()


@router.get("")
def list_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    accounts = db.query(Account).filter(Account.user_id == current_user.id).all()
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


@router.get("/{account_id}")
def get_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    account = (
        db.query(Account)
        .filter(Account.id == account_id, Account.user_id == current_user.id)
        .first()
    )
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    return {
        "id": account.id,
        "account_name": account.account_name,
        "account_type": account.account_type,
        "currency": account.currency,
        "balance": float(account.balance),
        "provider_name": account.provider.name,
    }
