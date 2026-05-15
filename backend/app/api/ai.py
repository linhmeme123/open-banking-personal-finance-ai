from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.ai.categorizer import categorize_transaction
from app.ai.coach import answer_personal_finance_question
from app.db.session import get_db
from app.models.domain import Transaction
from app.schemas.dto import CategorizeRequest, CategorizeResponse, ChatRequest, ChatResponse

router = APIRouter()


@router.post("/categorize", response_model=CategorizeResponse)
def categorize(payload: CategorizeRequest, db: Session = Depends(get_db)):
    tx = db.query(Transaction).filter(Transaction.id == payload.transaction_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    category, confidence = categorize_transaction(tx.description, tx.merchant_name)
    tx.category = category
    tx.category_confidence = confidence
    db.commit()

    return CategorizeResponse(
        transaction_id=tx.id,
        category=category,
        confidence=confidence,
    )


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    answer = answer_personal_finance_question(db, payload.user_id, payload.message)
    return ChatResponse(answer=answer)
