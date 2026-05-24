from datetime import datetime, timedelta
from decimal import Decimal


def get_mock_providers():
    return [
        {"code": "BANK_A", "name": "Bank A Sandbox"},
        {"code": "BANK_B", "name": "Bank B Sandbox"},
        {"code": "EWALLET_X", "name": "E-wallet X Sandbox"},
    ]


def get_mock_account(provider_code: str):
    accounts = {
        "BANK_A": {
            "account_name": "Bank A Main Checking",
            "account_type": "checking",
            "currency": "VND",
            "balance": Decimal("15000000"),
        },
        "BANK_B": {
            "account_name": "Bank B Savings",
            "account_type": "savings",
            "currency": "VND",
            "balance": Decimal("42000000"),
        },
        "EWALLET_X": {
            "account_name": "E-wallet X",
            "account_type": "wallet",
            "currency": "VND",
            "balance": Decimal("2500000"),
        },
    }
    return accounts[provider_code]


def get_mock_transactions(account_id: int, provider_code: str = "BANK_A"):
    now = datetime(2026, 5, 24, 12, 0, 0)
    suffix = provider_code.lower()
    return [
        {
            "account_id": account_id,
            "external_id": f"{suffix}-{account_id}-001",
            "transaction_time": now - timedelta(days=1),
            "description": "Highlands Coffee",
            "merchant_name": "Highlands Coffee",
            "amount": Decimal("-65000"),
            "currency": "VND",
            "direction": "expense",
        },
        {
            "account_id": account_id,
            "external_id": f"{suffix}-{account_id}-002",
            "transaction_time": now - timedelta(days=2),
            "description": "Grab Bike",
            "merchant_name": "Grab",
            "amount": Decimal("-42000"),
            "currency": "VND",
            "direction": "expense",
        },
        {
            "account_id": account_id,
            "external_id": f"{suffix}-{account_id}-003",
            "transaction_time": now - timedelta(days=3),
            "description": "Salary May",
            "merchant_name": "Company Payroll",
            "amount": Decimal("12000000"),
            "currency": "VND",
            "direction": "income",
        },
        {
            "account_id": account_id,
            "external_id": f"{suffix}-{account_id}-004",
            "transaction_time": now - timedelta(days=4),
            "description": "Shopee order",
            "merchant_name": "Shopee",
            "amount": Decimal("-350000"),
            "currency": "VND",
            "direction": "expense",
        },
        {
            "account_id": account_id,
            "external_id": f"{suffix}-{account_id}-005",
            "transaction_time": now - timedelta(days=31),
            "description": "Netflix subscription",
            "merchant_name": "Netflix",
            "amount": Decimal("-260000"),
            "currency": "VND",
            "direction": "expense",
        },
        {
            "account_id": account_id,
            "external_id": f"{suffix}-{account_id}-006",
            "transaction_time": now - timedelta(days=1),
            "description": "Netflix subscription",
            "merchant_name": "Netflix",
            "amount": Decimal("-260000"),
            "currency": "VND",
            "direction": "expense",
        },
    ]
