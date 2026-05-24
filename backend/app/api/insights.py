from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.domain import User
from app.services.insight_service import get_category_breakdown, get_monthly_summary, get_recurring_payments

router = APIRouter()


@router.get("/monthly-summary")
def monthly_summary(
    month: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_monthly_summary(db, user_id=current_user.id, month=month)


@router.get("/category-breakdown")
def category_breakdown(
    month: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_category_breakdown(db, user_id=current_user.id, month=month)


@router.get("/recurring-payments")
def recurring_payments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_recurring_payments(db, user_id=current_user.id)
