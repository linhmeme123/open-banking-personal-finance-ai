from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.ai.coach import answer_personal_finance_question, persist_chat_turn
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.chat_message import AiChatMessage
from app.models.user import User
from app.schemas.chat_message import AiChatMessageOut, ChatRequest, ChatResponse
from app.schemas.transaction import CategorizeRequest, CategorizeResponse
from app.services.transaction_service import categorize_user_transaction

router = APIRouter()

@router.post("/categorize", response_model=CategorizeResponse)
def categorize(
    payload: CategorizeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return CategorizeResponse(**categorize_user_transaction(db, current_user.id, payload.transaction_id))


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
