from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.account import Account
from app.models.bank import BankConnection, BankProvider
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.bank import ProviderConnectRequest, SyncRequest
from app.services.consent_service import create_consent_event
from app.services.open_banking_mock import get_mock_account, get_mock_providers, get_mock_transactions
from app.ai.categorizer import categorize_transaction

router = APIRouter()


@router.get("/providers")
def providers():
    return get_mock_providers()


def get_or_create_provider(db: Session, provider_code: str) -> BankProvider:
    provider_info = next((provider for provider in get_mock_providers() if provider["code"] == provider_code), None)
    if not provider_info:
        raise HTTPException(status_code=404, detail="Provider not found")

    provider = db.query(BankProvider).filter(BankProvider.code == provider_code).first()
    if not provider:
        provider = BankProvider(code=provider_info["code"], name=provider_info["name"])
        db.add(provider)
        db.commit()
        db.refresh(provider)
    return provider


@router.post("/connect")
def connect_provider(
    payload: ProviderConnectRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    provider = get_or_create_provider(db, payload.provider_code)
    connection = (
        db.query(BankConnection)
        .filter(BankConnection.user_id == current_user.id, BankConnection.provider_id == provider.id)
        .first()
    )

    if connection:
        connection.status = "connected"
        connection.consent_scope = payload.scope
    else:
        connection = BankConnection(
            user_id=current_user.id,
            provider_id=provider.id,
            status="connected",
            consent_scope=payload.scope,
        )
        db.add(connection)

    db.commit()
    db.refresh(connection)
    create_consent_event(db, current_user.id, provider.code, payload.scope, "granted")

    return {
        "id": connection.id,
        "provider_code": provider.code,
        "provider_name": provider.name,
        "status": connection.status,
        "consent_scope": connection.consent_scope,
        "last_synced_at": connection.last_synced_at.isoformat() if connection.last_synced_at else None,
    }


@router.post("/sync")
def sync_open_banking_data(
    payload: SyncRequest | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    provider_code = payload.provider_code if payload else "BANK_A"
    provider = get_or_create_provider(db, provider_code)
    connection = (
        db.query(BankConnection)
        .filter(BankConnection.user_id == current_user.id, BankConnection.provider_id == provider.id)
        .first()
    )
    if not connection:
        connection = BankConnection(
            user_id=current_user.id,
            provider_id=provider.id,
            status="connected",
            consent_scope="accounts:read transactions:read",
        )
        db.add(connection)
        db.commit()
        db.refresh(connection)
        create_consent_event(db, current_user.id, provider.code, connection.consent_scope, "granted")

    account = (
        db.query(Account)
        .filter(Account.user_id == current_user.id, Account.provider_id == provider.id)
        .first()
    )
    if not account:
        account_data = get_mock_account(provider.code)
        account = Account(
            user_id=current_user.id,
            provider_id=provider.id,
            **account_data,
        )
        db.add(account)
        db.commit()
        db.refresh(account)

    created = 0
    for item in get_mock_transactions(account.id, provider.code):
        existing = db.query(Transaction).filter(Transaction.external_id == item["external_id"]).first()
        if existing:
            continue

        category, confidence = categorize_transaction(item["description"], item.get("merchant_name"))
        tx = Transaction(**item, category=category, category_confidence=confidence)
        db.add(tx)
        created += 1

    connection.last_synced_at = datetime.utcnow()
    db.commit()
    return {"status": "synced", "created_transactions": created}
