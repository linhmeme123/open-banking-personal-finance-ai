import hashlib
import json
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.domain import ConsentEvent


def create_consent_event(db: Session, user_id: int, provider_code: str, scope: str, action: str) -> ConsentEvent:
    payload = {
        "user_id": user_id,
        "provider_code": provider_code,
        "scope": scope,
        "action": action,
        "timestamp": datetime.utcnow().isoformat(),
    }
    event_hash = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()

    event = ConsentEvent(
        user_id=user_id,
        provider_code=provider_code,
        scope=scope,
        action=action,
        event_hash=event_hash,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event
