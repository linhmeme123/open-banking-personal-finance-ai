from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.ai.categorizer import categorize_transaction
from app.models.account import Account
from app.models.bank import BankConnection, BankProvider
from app.models.transaction import Transaction
from app.services.consent_service import create_consent_event
from app.services.open_banking_mock import (
    get_mock_accounts,
    get_mock_provider,
    get_mock_providers,
    get_mock_transactions,
)


def serialize_provider(provider: dict):
    return provider


def serialize_connection(connection: BankConnection):
    return {
        "id": connection.id,
        "provider_code": connection.provider.code,
        "provider_name": connection.provider.name,
        "provider_type": connection.provider.provider_type,
        "logo_url": connection.provider.logo_url,
        "status": connection.status,
        "consent_scope": connection.consent_scope,
        "last_synced_at": connection.last_synced_at.isoformat() if connection.last_synced_at else None,
    }


def list_providers():
    return [serialize_provider(provider) for provider in get_mock_providers()]


def list_connections(db: Session, user_id: int):
    connections = (
        db.query(BankConnection)
        .join(BankProvider)
        .filter(BankConnection.user_id == user_id)
        .order_by(BankProvider.name.asc())
        .all()
    )
    return [serialize_connection(connection) for connection in connections]


def get_or_create_provider(db: Session, provider_code: str) -> BankProvider:
    provider_info = get_mock_provider(provider_code)
    if not provider_info:
        raise HTTPException(status_code=404, detail="Provider not found")

    provider = db.query(BankProvider).filter(BankProvider.code == provider_code).first()
    if not provider:
        provider = BankProvider(
            code=provider_info["code"],
            name=provider_info["name"],
            provider_type=provider_info["type"],
            logo_url=provider_info["logo_url"],
            status=provider_info["status"],
            supported_scopes=provider_info["supported_scopes"],
        )
        db.add(provider)
    else:
        provider.name = provider_info["name"]
        provider.provider_type = provider_info["type"]
        provider.logo_url = provider_info["logo_url"]
        provider.status = provider_info["status"]
        provider.supported_scopes = provider_info["supported_scopes"]
    db.commit()
    db.refresh(provider)
    return provider


def connect_provider(db: Session, user_id: int, provider_code: str, scope: str):
    provider = get_or_create_provider(db, provider_code)
    if provider.status != "available":
        raise HTTPException(status_code=409, detail="Provider is not available yet")

    connection = (
        db.query(BankConnection)
        .filter(BankConnection.user_id == user_id, BankConnection.provider_id == provider.id)
        .first()
    )
    if connection:
        connection.status = "connected"
        connection.consent_scope = scope
    else:
        connection = BankConnection(
            user_id=user_id,
            provider_id=provider.id,
            status="connected",
            consent_scope=scope,
        )
        db.add(connection)
    db.commit()
    db.refresh(connection)
    create_consent_event(db, user_id, provider.code, scope, "granted")
    return serialize_connection(connection)


def sync_provider(db: Session, user_id: int, provider_code: str):
    provider = get_or_create_provider(db, provider_code)
    connection = (
        db.query(BankConnection)
        .filter(BankConnection.user_id == user_id, BankConnection.provider_id == provider.id)
        .first()
    )
    if not connection:
        raise HTTPException(status_code=409, detail="Connect provider before syncing")

    created_accounts = 0
    created_transactions = 0
    for account_data in get_mock_accounts(provider.code):
        account = (
            db.query(Account)
            .filter(
                Account.user_id == user_id,
                Account.provider_id == provider.id,
                Account.account_name == account_data["account_name"],
            )
            .first()
        )
        if not account:
            account = Account(user_id=user_id, provider_id=provider.id, **account_data)
            db.add(account)
            db.commit()
            db.refresh(account)
            created_accounts += 1

        for item in get_mock_transactions(account.id, provider.code):
            if db.query(Transaction).filter(Transaction.external_id == item["external_id"]).first():
                continue
            category, confidence = categorize_transaction(item["description"], item.get("merchant_name"))
            db.add(Transaction(**item, category=category, category_confidence=confidence))
            created_transactions += 1

    connection.last_synced_at = datetime.utcnow()
    db.commit()
    return {
        "status": "synced",
        "provider_code": provider.code,
        "created_accounts": created_accounts,
        "created_transactions": created_transactions,
    }
