from datetime import datetime
from decimal import Decimal
from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.ai.categorizer import categorize_transaction
from app.integrations.banking.base import ProviderTransaction
from app.integrations.banking.registry import (
    get_provider_client,
    get_provider_definition,
    list_provider_definitions,
)
from app.models.account import Account
from app.models.bank import BankConnection, BankProvider
from app.models.transaction import Transaction
from app.models.user import User
from app.services.consent_service import create_consent_event


def serialize_connection(connection: BankConnection, db: Session):
    return {
        "id": connection.id,
        "provider_code": connection.provider.code,
        "provider_name": connection.provider.name,
        "provider_type": connection.provider.provider_type,
        "logo_url": connection.provider.logo_url,
        "status": connection.status,
        "consent_scope": connection.consent_scope,
        "last_synced_at": connection.last_synced_at.isoformat() if connection.last_synced_at else None,
        "connected_accounts_count": (
            db.query(Account)
            .filter(Account.user_id == connection.user_id, Account.provider_id == connection.provider_id)
            .count()
        ),
    }


def list_providers():
    return [definition.serialize() for definition in list_provider_definitions()]


def list_connections(db: Session, user_id: int):
    connections = (
        db.query(BankConnection)
        .join(BankProvider)
        .filter(BankConnection.user_id == user_id)
        .order_by(BankProvider.name.asc())
        .all()
    )
    return [serialize_connection(connection, db) for connection in connections]


def get_or_create_provider(db: Session, provider_code: str) -> BankProvider:
    definition = get_provider_definition(provider_code)
    provider = db.query(BankProvider).filter(BankProvider.code == definition.code).first()
    if not provider:
        provider = BankProvider(code=definition.code)
        db.add(provider)
    provider.name = definition.name
    provider.provider_type = definition.type
    provider.logo_url = definition.logo_url
    provider.status = definition.status
    provider.supported_scopes = list(definition.supported_scopes)
    db.commit()
    db.refresh(provider)
    return provider


def connect_provider(db: Session, user: User, provider_code: str, scope: str):
    provider = get_or_create_provider(db, provider_code)
    if provider.status != "available":
        raise HTTPException(status_code=409, detail="Provider is not available yet")

    client = get_provider_client(db, provider.code)
    result = client.connect(user, provider, scope)
    connection = (
        db.query(BankConnection)
        .filter(BankConnection.user_id == user.id, BankConnection.provider_id == provider.id)
        .first()
    )
    if connection:
        connection.status = result.status
        connection.consent_scope = scope
    else:
        connection = BankConnection(
            user_id=user.id,
            provider_id=provider.id,
            status=result.status,
            consent_scope=scope,
        )
        db.add(connection)
    db.commit()
    db.refresh(connection)
    create_consent_event(db, user.id, provider.code, scope, "granted")
    return serialize_connection(connection, db)


def disconnect_provider(db: Session, user_id: int, provider_code: str):
    provider = get_or_create_provider(db, provider_code)
    connection = (
        db.query(BankConnection)
        .filter(BankConnection.user_id == user_id, BankConnection.provider_id == provider.id)
        .first()
    )
    if not connection:
        raise HTTPException(status_code=404, detail="Provider connection not found")

    scope = connection.consent_scope
    db.delete(connection)
    db.commit()
    create_consent_event(db, user_id, provider.code, scope, "revoked")
    return {"status": "disconnected", "provider_code": provider.code}


def _upsert_account(db: Session, user_id: int, provider: BankProvider, provider_account) -> tuple[Account, bool]:
    account = (
        db.query(Account)
        .filter(
            Account.user_id == user_id,
            Account.provider_id == provider.id,
            Account.external_account_id == provider_account.external_account_id,
        )
        .first()
    )
    created = account is None
    if not account:
        account = Account(
            user_id=user_id,
            provider_id=provider.id,
            external_account_id=provider_account.external_account_id,
        )
        db.add(account)
    account.account_name = provider_account.account_name
    account.account_type = provider_account.account_type
    account.currency = provider_account.currency
    account.balance = provider_account.balance
    db.flush()
    return account, created


def _save_transaction(db: Session, account: Account, item: ProviderTransaction) -> tuple[bool, str | None]:
    if db.query(Transaction).filter(Transaction.external_id == item.external_transaction_id).first():
        return False, None
    category, confidence = categorize_transaction(item.description, item.merchant_name)
    db.add(
        Transaction(
            account_id=account.id,
            external_id=item.external_transaction_id,
            transaction_time=item.transaction_time,
            description=item.description,
            merchant_name=item.merchant_name,
            amount=item.amount,
            currency=item.currency,
            direction=item.direction,
            category=category,
            category_confidence=confidence,
        )
    )
    return True, category


def sync_provider(db: Session, user_id: int, provider_code: str):
    provider = get_or_create_provider(db, provider_code)
    connection = (
        db.query(BankConnection)
        .filter(BankConnection.user_id == user_id, BankConnection.provider_id == provider.id)
        .first()
    )
    if not connection:
        raise HTTPException(status_code=409, detail="Connect provider before syncing")

    client = get_provider_client(db, provider.code)
    accounts_synced = 0
    transactions_added = 0
    latest_balance = Decimal("0")
    for provider_account in client.get_accounts(connection):
        account, _ = _upsert_account(db, user_id, provider, provider_account)
        accounts_synced += 1
        latest_balance += provider_account.balance
        for item in client.get_transactions(connection, account, since=connection.last_synced_at):
            transaction_added, category = _save_transaction(db, account, item)
            transactions_added += int(transaction_added)
            if transaction_added:
                client.record_transaction_synced(item.external_transaction_id, category=category)

    connection.last_synced_at = datetime.utcnow()
    db.commit()
    return {
        "status": "synced",
        "provider_code": provider.code,
        "accounts_synced": accounts_synced,
        "transactions_added": transactions_added,
        "latest_balance": str(latest_balance),
        # Backward-compatible fields for the existing dashboard.
        "created_accounts": accounts_synced,
        "created_transactions": transactions_added,
    }


def process_transaction_webhook(
    db: Session,
    payload: dict[str, Any],
    headers: dict[str, str],
    *,
    user_id: int | None = None,
):
    provider_code = payload.get("provider_code")
    if not provider_code:
        raise HTTPException(status_code=422, detail="provider_code is required")
    definition = get_provider_definition(provider_code)
    provider_code = definition.code
    print("[webhook] received payload", payload)
    print("[webhook] provider_code", provider_code)
    client = get_provider_client(db, provider_code)
    if not client.verify_webhook(payload, headers):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    item = client.normalize_transaction(payload["transaction"])
    print(
        "[webhook] transaction",
        {
            "external_transaction_id": item.external_transaction_id,
            "external_account_id": item.external_account_id,
            "amount": str(item.amount),
            "direction": item.direction,
        },
    )
    client.record_webhook_verified(item.external_transaction_id)
    provider = get_or_create_provider(db, provider_code)
    accounts = (
        db.query(Account)
        .join(
            BankConnection,
            (BankConnection.user_id == Account.user_id)
            & (BankConnection.provider_id == Account.provider_id),
        )
        .filter(
            Account.provider_id == provider.id,
            Account.external_account_id == item.external_account_id,
            BankConnection.status == "connected",
        )
    )
    if user_id is not None:
        accounts = accounts.filter(Account.user_id == user_id)
    matched_accounts = accounts.order_by(Account.id.asc()).all()
    if len(matched_accounts) > 1:
        raise HTTPException(status_code=409, detail="Webhook account owner is ambiguous")
    account = matched_accounts[0] if matched_accounts else None
    connection = None
    if account:
        connection = (
            db.query(BankConnection)
            .filter(
                BankConnection.user_id == account.user_id,
                BankConnection.provider_id == provider.id,
                BankConnection.status == "connected",
            )
            .first()
        )
    else:
        connections = db.query(BankConnection).filter(
            BankConnection.provider_id == provider.id,
            BankConnection.status == "connected",
        )
        if user_id is not None:
            connections = connections.filter(BankConnection.user_id == user_id)
        matched_connections = connections.order_by(BankConnection.id.asc()).all()
        if not matched_connections:
            raise HTTPException(status_code=409, detail="Connect provider before pushing bank events")
        if len(matched_connections) > 1:
            raise HTTPException(status_code=409, detail="Webhook account owner is ambiguous")
        connection = matched_connections[0]
    print("[webhook] matched connection", {"connection_id": connection.id, "user_id": connection.user_id})

    account_created = account is None
    if not account:
        provider_account = next(
            (
                provider_account
                for provider_account in client.get_accounts(connection)
                if provider_account.external_account_id == item.external_account_id
            ),
            None,
        )
        if not provider_account:
            raise HTTPException(status_code=404, detail="Webhook account was not found at the provider")
        account, _ = _upsert_account(db, connection.user_id, provider, provider_account)
        print("[webhook] created account", {"account_id": account.id, "external_account_id": item.external_account_id})

    transaction_added, category = _save_transaction(db, account, item)
    transactions_added = int(transaction_added)
    if transactions_added:
        balance_before = account.balance
        if not account_created:
            account.balance += item.amount
        print("[webhook] created transaction", {"external_transaction_id": item.external_transaction_id})
        print("[webhook] categorized", {"category": category})
        client.record_transaction_synced(item.external_transaction_id, category=category)
        client.record_balance_updated(
            item.external_transaction_id,
            balance_before=balance_before,
            balance_after=account.balance,
            currency=account.currency,
        )
        print("[webhook] updated balance", {"before": str(balance_before), "after": str(account.balance)})
    else:
        client.record_transaction_synced(item.external_transaction_id)
    db.commit()
    return {
        "status": "accepted" if transaction_added else "already_synced",
        "provider_code": provider_code,
        "transactions_added": transactions_added,
    }
