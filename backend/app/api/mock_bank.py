from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.mock_bank import (
    MockBankAccountCreate,
    MockBankGenerateRequest,
    MockBankTransactionCreate,
    MockBankWebhookSendRequest,
)
from app.services import mock_bank_service

router = APIRouter()


@router.get("/providers")
def providers():
    return mock_bank_service.list_mock_providers()


@router.get("/accounts")
def accounts(provider_code: str = Query(...), db: Session = Depends(get_db)):
    return mock_bank_service.list_accounts(db, provider_code)


@router.post("/accounts")
def create_account(payload: MockBankAccountCreate, db: Session = Depends(get_db)):
    values = payload.model_dump(exclude={"provider_code"})
    return mock_bank_service.create_account(db, payload.provider_code, **values)


@router.get("/transactions")
def transactions(
    provider_code: str = Query(...),
    external_account_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return mock_bank_service.list_transactions(db, provider_code, external_account_id)


@router.post("/transactions")
def create_transaction(payload: MockBankTransactionCreate, db: Session = Depends(get_db)):
    values = payload.model_dump(exclude={"provider_code"})
    return mock_bank_service.create_transaction(db, payload.provider_code, **values)


@router.post("/transactions/generate")
def generate_transaction(payload: MockBankGenerateRequest, db: Session = Depends(get_db)):
    return mock_bank_service.generate_transaction(db, payload.provider_code, payload.external_account_id)


@router.get("/transactions/{external_transaction_id}/events")
def transaction_events(
    external_transaction_id: str,
    provider_code: str = Query(...),
    db: Session = Depends(get_db),
):
    return mock_bank_service.list_transaction_events(db, provider_code, external_transaction_id)


@router.post("/webhooks/send")
def send_webhook(
    payload: MockBankWebhookSendRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return mock_bank_service.send_webhook(db, payload.provider_code, payload.external_transaction_id, current_user.id)
