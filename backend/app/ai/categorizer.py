def categorize_transaction(description: str, merchant_name: str | None = None) -> tuple[str, float]:
    text = f"{description} {merchant_name or ''}".lower()

    rules = [
        (["coffee", "highlands", "starbucks", "phuc long", "cafe"], "food_drink", 0.92),
        (["grab", "be", "taxi", "bus", "metro"], "transport", 0.90),
        (["salary", "payroll", "lương"], "income", 0.95),
        (["shopee", "lazada", "tiki"], "shopping", 0.88),
        (["netflix", "spotify", "icloud", "subscription"], "subscription", 0.86),
        (["electric", "water", "internet", "utility"], "bills", 0.84),
    ]

    for keywords, category, confidence in rules:
        if any(keyword in text for keyword in keywords):
            return category, confidence

    return "others", 0.55
