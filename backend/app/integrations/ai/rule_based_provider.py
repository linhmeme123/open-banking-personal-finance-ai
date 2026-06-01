from datetime import datetime

from app.integrations.ai.base import AIProvider


NO_SYNCED_DATA_MESSAGE = "Bạn chưa có đủ dữ liệu đã đồng bộ để phân tích. Hãy đồng bộ tài khoản ngân hàng trước."


def _format_money(amount: float, currency: str = "VND") -> str:
    return f"{amount:,.0f} {currency}"


def _sum_currency_values(values: dict[str, float]) -> str:
    if not values:
        return "0 VND"
    return ", ".join(_format_money(amount, currency) for currency, amount in values.items())


class RuleBasedAIProvider(AIProvider):
    provider_name = "rule_based"

    def generate_answer(
        self,
        message: str,
        financial_context: dict,
        chat_history: list[dict] | None = None,
    ) -> str:
        if not financial_context.get("synced_data_available"):
            return NO_SYNCED_DATA_MESSAGE

        normalized_message = message.casefold()
        top_categories = financial_context.get("top_categories", [])
        recent_transactions = financial_context.get("recent_transactions", [])
        recurring_merchants = financial_context.get("recurring_merchants", [])
        budgets = financial_context.get("budgets", [])

        if any(
            keyword in normalized_message
            for keyword in ("số dư", "số tiền hiện có", "còn bao nhiêu tiền", "balance")
        ):
            return f"Số dư hiện tại của bạn là {_sum_currency_values(financial_context.get('total_balance', {}))}."

        if any(keyword in normalized_message for keyword in ("nhiều nhất", "top", "lớn nhất", "vào đâu")):
            if not top_categories:
                return "Tháng này chưa có đủ giao dịch chi tiêu để xác định nhóm lớn nhất."
            top = top_categories[0]
            return f"Tháng này bạn chi nhiều nhất cho {top['category']}: {_format_money(top['amount'], top['currency'])}."

        if any(keyword in normalized_message for keyword in ("hôm nay", "today")):
            today = datetime.utcnow().date().isoformat()
            todays_expenses = [
                transaction
                for transaction in recent_transactions
                if transaction["date"] == today and transaction["direction"] == "expense"
            ]
            if not todays_expenses:
                return "Hôm nay chưa có khoản chi nào trong dữ liệu đã đồng bộ."
            items = "; ".join(
                f"{transaction['description']}: {_format_money(transaction['amount'], transaction['currency'])}"
                for transaction in todays_expenses[:5]
            )
            return f"Hôm nay bạn đã chi: {items}."

        if any(keyword in normalized_message for keyword in ("bất thường", "bất thuong", "unusual")):
            expenses = [transaction for transaction in recent_transactions if transaction["direction"] == "expense"]
            if len(expenses) < 3:
                return "Chưa có đủ giao dịch để nhận diện khoản chi bất thường."
            average = sum(transaction["amount"] for transaction in expenses) / len(expenses)
            unusual = [transaction for transaction in expenses if transaction["amount"] >= average * 2]
            if not unusual:
                return "Chưa thấy khoản chi nào cao bất thường trong các giao dịch gần đây."
            largest = max(unusual, key=lambda transaction: transaction["amount"])
            return (
                f"Khoản chi cần chú ý là {largest['description']}: "
                f"{_format_money(largest['amount'], largest['currency'])}, cao hơn đáng kể so với giao dịch gần đây."
            )

        if any(keyword in normalized_message for keyword in ("tiết kiệm", "tiết kiem", "save", "saving")):
            if budgets:
                tightest = min(budgets, key=lambda budget: budget["monthly_limit"] - budget["spent"])
                remaining = tightest["monthly_limit"] - tightest["spent"]
                return (
                    f"Hãy ưu tiên theo dõi ngân sách {tightest['category']}. "
                    f"Bạn còn {_format_money(remaining)} trong hạn mức tháng này."
                )
            if top_categories:
                top = top_categories[0]
                return (
                    f"Bạn có thể bắt đầu bằng cách giảm 10% chi tiêu cho {top['category']}, "
                    f"tương đương khoảng {_format_money(top['amount'] * 0.1, top['currency'])} mỗi tháng."
                )
            return "Chưa có đủ giao dịch chi tiêu để đề xuất mục tiêu tiết kiệm cụ thể."

        recurring_hint = ""
        if recurring_merchants:
            merchant = recurring_merchants[0]
            recurring_hint = f" Khoản lặp lại đáng chú ý: {merchant['merchant']} ({merchant['occurrences']} lần)."
        return (
            f"Tháng này, thu nhập của bạn là {_sum_currency_values(financial_context.get('monthly_income', {}))}; "
            f"chi tiêu là {_sum_currency_values(financial_context.get('monthly_expense', {}))}; "
            f"số dư hiện tại là {_sum_currency_values(financial_context.get('total_balance', {}))}."
            f"{recurring_hint}"
        )
