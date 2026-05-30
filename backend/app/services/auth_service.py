from datetime import datetime

from fastapi import HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_refresh_token_expiry,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.models.auth_token import AuthToken
from app.models.user import User
from app.schemas.auth import LoginRequest, SignupRequest


def create_auth_session(db: Session, user: User, request: Request):
    access_token, access_token_jti = create_access_token(user.id)
    refresh_token = create_refresh_token()

    auth_token = AuthToken(
        user_id=user.id,
        access_token_jti=access_token_jti,
        refresh_token_hash=hash_refresh_token(refresh_token),
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
        expires_at=get_refresh_token_expiry(),
    )

    db.add(auth_token)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user,
    }


def signup(db: Session, data: SignupRequest, request: Request):
    existing_user = db.query(User).filter(User.email == data.email).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = User(
        full_name=data.full_name,
        email=data.email,
        hashed_password=hash_password(data.password),
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return create_auth_session(db, user, request)


def login(db: Session, data: LoginRequest, request: Request):
    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    return create_auth_session(db, user, request)


def refresh_access_token(db: Session, refresh_token: str):
    refresh_token_hash = hash_refresh_token(refresh_token)

    auth_token = (
        db.query(AuthToken)
        .filter(AuthToken.refresh_token_hash == refresh_token_hash)
        .first()
    )

    if not auth_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    if auth_token.expires_at < datetime.utcnow():
        db.delete(auth_token)
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired",
        )

    user = db.query(User).filter(User.id == auth_token.user_id).first()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    access_token, access_token_jti = create_access_token(user.id)

    auth_token.access_token_jti = access_token_jti
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user,
    }


def logout(db: Session, access_token_jti: str):
    auth_token = (
        db.query(AuthToken)
        .filter(AuthToken.access_token_jti == access_token_jti)
        .first()
    )

    if auth_token:
        db.delete(auth_token)
        db.commit()

    return {"message": "Logged out successfully"}