def categorize_transaction(description: str, merchant_name: str | None = None) -> tuple[str, float]:
    """Rule-based MVP categorizer with an interface ready for an AI implementation."""
    text = f"{description} {merchant_name or ''}".lower()

    rules = [
        (["coffee", "highlands", "starbucks", "phuc long", "cafe", "restaurant"], "food", 0.94),
        (["grocery", "supermarket", "winmart", "coopmart", "bach hoa"], "groceries", 0.92),
        (["grab", "be ", "taxi", "bus", "metro", "bike", "đạp xe", "dap xe"], "transport", 0.93),
        (["salary", "payroll", "luong"], "salary", 0.98),
        (["transfer", "chuyen khoan", "bank transfer"], "transfer", 0.90),
        (["shopee", "lazada", "tiki"], "shopping", 0.91),
        (["netflix", "spotify", "cinema", "movie", "subscription"], "entertainment", 0.89),
        (["electric", "water", "internet", "utility", "vnpt"], "bills", 0.91),
        (["pharmacy", "hospital", "clinic", "doctor"], "healthcare", 0.93),
        (["school", "tuition", "course", "education"], "education", 0.88),
        (["investment", "fund", "stock", "saving"], "investment", 0.87),
    ]

    for keywords, category, confidence in rules:
        if any(keyword in text for keyword in keywords):
            return category, confidence

    return "unknown", 0.50
