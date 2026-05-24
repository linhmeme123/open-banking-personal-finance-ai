from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.db.session import get_db
from app.models.domain import User
from app.schemas.dto import LoginResponse

router = APIRouter()


@router.post("/demo-login", response_model=LoginResponse)
def demo_login(db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == "demo@pfai.local").first()
    if not user:
        user = User(full_name="Demo User", email="demo@pfai.local")
        db.add(user)
        db.commit()
        db.refresh(user)

    return LoginResponse(access_token=create_access_token(user.id), user=user)

