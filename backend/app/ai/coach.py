from decimal import Decimal
from sqlalchemy.orm import Session

from app.models.domain import Transaction


def answer_personal_finance_question(db: Session, user_id: int, message: str) -> str:
    # Starter mock: thay phần này bằng LLM + function calling ở giai đoạn sau.
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

    return (
        f"Trong dữ liệu hiện tại, tổng chi tiêu của bạn là khoảng {total_expense:,.0f} VND. "
        f"Nhóm chi tiêu lớn nhất là '{top_category[0]}' với {top_category[1]:,.0f} VND. "
        "Gợi ý: bạn nên đặt ngân sách theo category và theo dõi các khoản lặp lại như subscription, ăn uống, di chuyển."
    )
