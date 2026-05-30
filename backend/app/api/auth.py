from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.deps import get_current_token_jti, get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    SignupRequest,
)
from app.schemas.user import UserOut
from app.services.auth_service import (
    login,
    logout,
    refresh_access_token,
    signup,
)


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup", response_model=LoginResponse)
def signup_user(
    data: SignupRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    return signup(db, data, request)


@router.post("/login", response_model=LoginResponse)
def login_user(
    data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    return login(db, data, request)


@router.post("/refresh", response_model=LoginResponse)
def refresh_token(
    data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    return refresh_access_token(db, data.refresh_token)


@router.post("/logout")
def logout_user(
    token_jti: str = Depends(get_current_token_jti),
    db: Session = Depends(get_db),
):
    return logout(db, token_jti)


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user