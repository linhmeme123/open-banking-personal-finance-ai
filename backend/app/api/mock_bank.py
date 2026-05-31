from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.integrations.banking import fake_bank_store
from app.integrations.banking.registry import list_provider_definitions
from app.schemas.mock_bank import (
    MockBankAccountCreate,
    MockBankGenerateRequest,
    MockBankTransactionCreate,
    MockBankWebhookSendRequest,
)
from app.services.open_banking_service import process_transaction_webhook

router = APIRouter()


def serialize(item: dict):
    return {key: value.isoformat() if hasattr(value, "isoformat") else value for key, value in item.items()}


@router.get("/providers")
def providers():
    return [
        definition.serialize()
        for definition in list_provider_definitions()
        if definition.mock_console
    ]


@router.get("/accounts")
def accounts(provider_code: str = Query(...)):
    return [serialize(item) for item in fake_bank_store.list_accounts(provider_code)]


@router.post("/accounts")
def create_account(payload: MockBankAccountCreate):
    return serialize(fake_bank_store.create_account(**payload.model_dump()))


@router.get("/transactions")
def transactions(provider_code: str = Query(...), external_account_id: str | None = Query(default=None)):
    return [serialize(item) for item in fake_bank_store.list_transactions(provider_code, external_account_id)]


@router.post("/transactions")
def create_transaction(payload: MockBankTransactionCreate):
    return serialize(fake_bank_store.create_transaction(**payload.model_dump()))


@router.post("/transactions/generate")
def generate_transaction(payload: MockBankGenerateRequest):
    return serialize(fake_bank_store.generate_transaction(**payload.model_dump()))


@router.post("/webhooks/send")
def send_webhook(payload: MockBankWebhookSendRequest, db: Session = Depends(get_db)):
    transaction = fake_bank_store.get_transaction(payload.provider_code, payload.external_transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Mock transaction not found")
    return process_transaction_webhook(
        db,
        {"provider_code": payload.provider_code, "transaction": transaction},
        {"x-fake-bank-signature": "velora-fake-bank"},
    )
