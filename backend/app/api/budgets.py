from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.budget import Budget
from app.models.user import User
from app.schemas.budget import BudgetCreate, BudgetOut

router = APIRouter()


@router.get("", response_model=list[BudgetOut])
def list_budgets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Budget)
        .filter(Budget.user_id == current_user.id)
        .order_by(Budget.month.desc(), Budget.category.asc())
        .all()
    )


@router.post("", response_model=BudgetOut)
def create_budget(
    payload: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    budget = (
        db.query(Budget)
        .filter(
            Budget.user_id == current_user.id,
            Budget.category == payload.category,
            Budget.month == payload.month,
        )
        .first()
    )
    if budget:
        budget.monthly_limit = payload.monthly_limit
    else:
        budget = Budget(
            user_id=current_user.id,
            category=payload.category,
            month=payload.month,
            monthly_limit=payload.monthly_limit,
        )
        db.add(budget)

    db.commit()
    db.refresh(budget)
    return budget
