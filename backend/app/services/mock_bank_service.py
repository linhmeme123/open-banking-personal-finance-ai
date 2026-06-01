from typing import Any, Callable

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.integrations.banking.base import BankProviderClient
from app.integrations.banking.registry import (
    get_provider_client,
    get_provider_definition,
    list_provider_definitions,
)
from app.services.open_banking_service import process_transaction_webhook


def serialize(item: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value.isoformat() if hasattr(value, "isoformat") else value
        for key, value in item.items()
    }


def list_mock_providers():
    return [
        definition.serialize()
        for definition in list_provider_definitions()
        if definition.mock_console
    ]


def _get_mock_client(db: Session, provider_code: str) -> BankProviderClient:
    definition = get_provider_definition(provider_code)
    if not definition.mock_console:
        raise HTTPException(status_code=409, detail="Provider does not expose a mock bank console")
    return get_provider_client(db, provider_code)


def _run_console_operation(operation: Callable[[], Any]):
    try:
        return operation()
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except NotImplementedError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


def list_accounts(db: Session, provider_code: str):
    client = _get_mock_client(db, provider_code)
    return [serialize(item) for item in _run_console_operation(client.list_mock_accounts)]


def create_account(db: Session, provider_code: str, **values: Any):
    client = _get_mock_client(db, provider_code)
    return serialize(_run_console_operation(lambda: client.create_mock_account(**values)))


def list_transactions(db: Session, provider_code: str, external_account_id: str | None = None):
    client = _get_mock_client(db, provider_code)
    return [
        serialize(item)
        for item in _run_console_operation(lambda: client.list_mock_transactions(external_account_id))
    ]


def create_transaction(db: Session, provider_code: str, **values: Any):
    client = _get_mock_client(db, provider_code)
    return serialize(_run_console_operation(lambda: client.create_mock_transaction(**values)))


def generate_transaction(db: Session, provider_code: str, external_account_id: str):
    client = _get_mock_client(db, provider_code)
    return serialize(_run_console_operation(lambda: client.generate_mock_transaction(external_account_id)))


def list_transaction_events(db: Session, provider_code: str, external_transaction_id: str):
    client = _get_mock_client(db, provider_code)
    transaction = _run_console_operation(lambda: client.get_mock_transaction(external_transaction_id))
    if not transaction:
        raise HTTPException(status_code=404, detail="Mock transaction not found")
    return [
        serialize(event)
        for event in _run_console_operation(lambda: client.list_mock_transaction_events(external_transaction_id))
    ]


def send_webhook(db: Session, provider_code: str, external_transaction_id: str, user_id: int):
    client = _get_mock_client(db, provider_code)
    transaction = _run_console_operation(lambda: client.get_mock_transaction(external_transaction_id))
    if not transaction:
        raise HTTPException(status_code=404, detail="Mock transaction not found")

    print(
        "[mock-bank] send webhook",
        {
            "provider_code": provider_code,
            "mock_transaction_id": external_transaction_id,
            "external_transaction_id": transaction["external_transaction_id"],
            "external_account_id": transaction["external_account_id"],
            "amount": str(transaction["amount"]),
            "direction": transaction["direction"],
        },
    )
    client.record_webhook_sent(external_transaction_id)
    try:
        return process_transaction_webhook(
            db,
            {"provider_code": provider_code, "transaction": transaction},
            client.get_webhook_headers(),
            user_id=user_id,
        )
    except Exception as exc:
        reason = exc.detail if isinstance(exc, HTTPException) else str(exc)
        client.record_transaction_failed(external_transaction_id, reason)
        raise
