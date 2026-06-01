from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.bank import ProviderConnectRequest, SyncRequest
from app.services.open_banking_service import (
    connect_provider,
    disconnect_provider,
    list_connections,
    list_providers,
    sync_provider,
)

router = APIRouter()


@router.get("/providers")
def providers():
    return list_providers()


@router.get("/connections")
def connections(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_connections(db, current_user.id)


@router.post("/connect")
def connect(
    payload: ProviderConnectRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return connect_provider(db, current_user, payload.provider_code, payload.scope)


@router.post("/sync")
def sync(
    payload: SyncRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return sync_provider(db, current_user.id, payload.provider_code)


@router.post("/disconnect")
def disconnect(
    payload: SyncRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return disconnect_provider(db, current_user.id, payload.provider_code)
