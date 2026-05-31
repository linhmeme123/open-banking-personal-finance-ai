from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.account import Account
from app.models.bank import BankProvider
from app.models.user import User

router = APIRouter()


def serialize_account(account: Account):
    return {
        "id": account.id,
        "account_name": account.account_name,
        "account_type": account.account_type,
        "currency": account.currency,
        "balance": float(account.balance),
        "provider_code": account.provider.code,
        "provider_name": account.provider.name,
        "provider_type": account.provider.provider_type,
    }


@router.get("")
def list_accounts(
    provider_code: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Account).join(BankProvider).filter(Account.user_id == current_user.id)
    if provider_code:
        query = query.filter(BankProvider.code == provider_code)
    return [serialize_account(account) for account in query.order_by(BankProvider.name, Account.account_name).all()]


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
    return serialize_account(account)
