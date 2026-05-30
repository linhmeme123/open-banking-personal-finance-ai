from decimal import Decimal
from sqlalchemy.orm import Session

from app.models.chat_message import AiChatMessage
from app.models.transaction import Transaction
from app.services.insight_service import get_budget_status, get_recurring_payments


def answer_personal_finance_question(db: Session, user_id: int, message: str) -> str:
    transactions = (
        db.query(Transaction)
        .join(Transaction.account)
        .filter(Transaction.account.has(user_id=user_id))
        .all()
    )

    total_expense = sum(
        abs(t.amount) for t in transactions if t.direction == "expense"
    ) or Decimal("0")

    by_category: dict[str, Decimal] = {}
    for tx in transactions:
        if tx.direction == "expense":
            category = tx.category or "uncategorized"
            by_category[category] = by_category.get(category, Decimal("0")) + abs(tx.amount)

    if not transactions:
        return "Bạn chưa có dữ liệu giao dịch. Hãy sync dữ liệu Open Banking trước."

    top_category = max(by_category.items(), key=lambda item: item[1], default=("none", Decimal("0")))
    recurring = get_recurring_payments(db, user_id)
    budgets = get_budget_status(db, user_id)
    recurring_hint = ""
    if recurring:
        recurring_hint = f" Khoản lặp lại đáng chú ý: {recurring[0]['merchant_name']} khoảng {recurring[0]['amount']:,.0f} VND."
    budget_hint = ""
    if budgets:
        tight_budget = min(budgets, key=lambda item: item["remaining"])
        budget_hint = (
            f" Ngân sách cần theo dõi nhất là {tight_budget['category']}: "
            f"đã chi {tight_budget['spent']:,.0f}/{tight_budget['monthly_limit']:,.0f} VND."
        )

    return (
        f"Trong dữ liệu hiện tại, tổng chi tiêu của bạn là khoảng {total_expense:,.0f} VND. "
        f"Nhóm chi tiêu lớn nhất là '{top_category[0]}' với {top_category[1]:,.0f} VND. "
        "Gợi ý: bạn nên đặt ngân sách theo category và theo dõi các khoản lặp lại như subscription, ăn uống, di chuyển."
        f"{recurring_hint}{budget_hint}"
    )


def persist_chat_turn(db: Session, user_id: int, message: str, answer: str):
    db.add(AiChatMessage(user_id=user_id, role="user", content=message))
    db.add(AiChatMessage(user_id=user_id, role="assistant", content=answer))
    db.commit()
