from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.domain import ConsentEvent
from app.schemas.dto import ConsentCreate
from app.services.consent_service import create_consent_event

router = APIRouter()


@router.post("")
def create_consent(payload: ConsentCreate, db: Session = Depends(get_db)):
    event = create_consent_event(
        db=db,
        user_id=payload.user_id,
        provider_code=payload.provider_code,
        scope=payload.scope,
        action=payload.action,
    )
    return {
        "id": event.id,
        "provider_code": event.provider_code,
        "scope": event.scope,
        "action": event.action,
        "event_hash": event.event_hash,
        "created_at": event.created_at.isoformat(),
    }


@router.get("")
def list_consents(db: Session = Depends(get_db)):
    events = db.query(ConsentEvent).order_by(ConsentEvent.created_at.desc()).all()
    return [
        {
            "id": event.id,
            "provider_code": event.provider_code,
            "scope": event.scope,
            "action": event.action,
            "event_hash": event.event_hash,
            "created_at": event.created_at.isoformat(),
        }
        for event in events
    ]
