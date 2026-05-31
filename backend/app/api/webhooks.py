from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.mock_bank import BankWebhookPayload
from app.services.open_banking_service import process_transaction_webhook

router = APIRouter()


@router.post("/bank/transactions")
def bank_transaction_webhook(payload: BankWebhookPayload, request: Request, db: Session = Depends(get_db)):
    return process_transaction_webhook(db, payload.model_dump(), dict(request.headers))
