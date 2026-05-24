from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.ai.categorizer import categorize_transaction
from app.ai.coach import answer_personal_finance_question, persist_chat_turn
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.domain import Account, AiChatMessage, Transaction, User
from app.schemas.dto import AiChatMessageOut, CategorizeRequest, CategorizeResponse, ChatRequest, ChatResponse

router = APIRouter()


@router.post("/categorize", response_model=CategorizeResponse)
def categorize(
    payload: CategorizeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tx = (
        db.query(Transaction)
        .join(Account)
        .filter(Transaction.id == payload.transaction_id, Account.user_id == current_user.id)
        .first()
    )
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
def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    answer = answer_personal_finance_question(db, current_user.id, payload.message)
    persist_chat_turn(db, current_user.id, payload.message, answer)
    return ChatResponse(answer=answer)


@router.get("/chat/history", response_model=list[AiChatMessageOut])
def chat_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(AiChatMessage)
        .filter(AiChatMessage.user_id == current_user.id)
        .order_by(AiChatMessage.created_at.asc(), AiChatMessage.id.asc())
        .all()
    )
