from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.insight_service import get_monthly_summary

router = APIRouter()


@router.get("/monthly-summary")
def monthly_summary(user_id: int = 1, db: Session = Depends(get_db)):
    return get_monthly_summary(db, user_id=user_id)
