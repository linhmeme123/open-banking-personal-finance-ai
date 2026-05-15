from datetime import datetime, timedelta
from decimal import Decimal


def get_mock_providers():
    return [
        {"code": "BANK_A", "name": "Bank A Sandbox"},
        {"code": "BANK_B", "name": "Bank B Sandbox"},
        {"code": "EWALLET_X", "name": "E-wallet X Sandbox"},
    ]


def get_mock_transactions(account_id: int):
    now = datetime.utcnow()
    return [
        {
            "account_id": account_id,
            "external_id": f"mock-{account_id}-001",
            "transaction_time": now - timedelta(days=1),
            "description": "Highlands Coffee",
            "merchant_name": "Highlands Coffee",
            "amount": Decimal("-65000"),
            "currency": "VND",
            "direction": "expense",
        },
        {
            "account_id": account_id,
            "external_id": f"mock-{account_id}-002",
            "transaction_time": now - timedelta(days=2),
            "description": "Grab Bike",
            "merchant_name": "Grab",
            "amount": Decimal("-42000"),
            "currency": "VND",
            "direction": "expense",
        },
        {
            "account_id": account_id,
            "external_id": f"mock-{account_id}-003",
            "transaction_time": now - timedelta(days=3),
            "description": "Salary May",
            "merchant_name": "Company Payroll",
            "amount": Decimal("12000000"),
            "currency": "VND",
            "direction": "income",
        },
        {
            "account_id": account_id,
            "external_id": f"mock-{account_id}-004",
            "transaction_time": now - timedelta(days=4),
            "description": "Shopee order",
            "merchant_name": "Shopee",
            "amount": Decimal("-350000"),
            "currency": "VND",
            "direction": "expense",
        },
    ]
