from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.bank import ProviderAuthorizeRequest, ProviderConnectRequest, SyncRequest
from app.services.open_banking_service import (
    authorize_connection,
    complete_connection,
    disconnect_provider,
    initiate_connection,
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
    return initiate_connection(db, current_user, payload.provider_code)


@router.post("/connect/initiate")
def initiate(
    payload: ProviderConnectRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return initiate_connection(db, current_user, payload.provider_code)


@router.post("/connect/authorize")
def authorize(
    payload: ProviderAuthorizeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return authorize_connection(
        db,
        current_user,
        payload.provider_code,
        {
            "username": payload.username,
            "customer_id": payload.customer_id,
            "account_number": payload.account_number,
            "otp_code": payload.otp_code,
        },
        payload.scopes,
        payload.selected_account_ids,
    )


@router.post("/connect/complete")
def complete(
    payload: ProviderConnectRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return complete_connection(db, current_user.id, payload.provider_code)


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
