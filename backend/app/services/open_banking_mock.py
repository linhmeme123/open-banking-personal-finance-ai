from datetime import datetime, timedelta
from decimal import Decimal


DEFAULT_SCOPES = ["accounts:read", "transactions:read", "balance:read"]


PROVIDERS = [
    {"code": "TIMO", "name": "Timo", "type": "digital_bank", "logo_url": None, "status": "available"},
    {"code": "CAKE", "name": "Cake", "type": "digital_bank", "logo_url": None, "status": "available"},
    {"code": "MOMO", "name": "MoMo", "type": "fintech", "logo_url": None, "status": "available"},
    {"code": "ZALOPAY", "name": "ZaloPay", "type": "fintech", "logo_url": None, "status": "available"},
    {"code": "VIETCOMBANK", "name": "Vietcombank", "type": "traditional_bank", "logo_url": None, "status": "available"},
    {"code": "TECHCOMBANK", "name": "Techcombank", "type": "traditional_bank", "logo_url": None, "status": "available"},
    {"code": "MB_BANK", "name": "MB Bank", "type": "traditional_bank", "logo_url": None, "status": "coming_soon"},
]


def get_mock_providers():
    return [{**provider, "supported_scopes": DEFAULT_SCOPES} for provider in PROVIDERS]


def get_mock_provider(provider_code: str):
    return next((provider for provider in get_mock_providers() if provider["code"] == provider_code), None)


def get_mock_accounts(provider_code: str):
    provider_accounts = {
        "TIMO": [
            ("Timo Spend Account", "checking", "18450000"),
            ("Timo Goal Save", "savings", "6200000"),
        ],
        "CAKE": [("Cake Everyday Account", "checking", "12750000")],
        "MOMO": [("MoMo Wallet", "wallet", "2850000")],
        "ZALOPAY": [("ZaloPay Wallet", "wallet", "1740000")],
        "VIETCOMBANK": [
            ("Vietcombank Current Account", "checking", "31800000"),
            ("Vietcombank Savings", "savings", "85000000"),
        ],
        "TECHCOMBANK": [
            ("Techcombank Everyday Account", "checking", "26800000"),
            ("Techcombank Savings", "savings", "54000000"),
        ],
        "MB_BANK": [("MB Bank Current Account", "checking", "22500000")],
    }
    return [
        {
            "account_name": name,
            "account_type": account_type,
            "currency": "VND",
            "balance": Decimal(balance),
        }
        for name, account_type, balance in provider_accounts[provider_code]
    ]


def get_mock_transactions(account_id: int, provider_code: str):
    now = datetime.utcnow().replace(microsecond=0)
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
            "description": "Salary Payroll",
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
            "transaction_time": now - timedelta(days=5),
            "description": "Internet bill",
            "merchant_name": "VNPT Internet",
            "amount": Decimal("-220000"),
            "currency": "VND",
            "direction": "expense",
        },
        {
            "account_id": account_id,
            "external_id": f"{suffix}-{account_id}-006",
            "transaction_time": now - timedelta(days=6),
            "description": "Pharmacy purchase",
            "merchant_name": "Long Chau Pharmacy",
            "amount": Decimal("-180000"),
            "currency": "VND",
            "direction": "expense",
        },
        {
            "account_id": account_id,
            "external_id": f"{suffix}-{account_id}-007",
            "transaction_time": now - timedelta(days=31),
            "description": "Netflix subscription",
            "merchant_name": "Netflix",
            "amount": Decimal("-260000"),
            "currency": "VND",
            "direction": "expense",
        },
        {
            "account_id": account_id,
            "external_id": f"{suffix}-{account_id}-008",
            "transaction_time": now - timedelta(days=1),
            "description": "Netflix subscription",
            "merchant_name": "Netflix",
            "amount": Decimal("-260000"),
            "currency": "VND",
            "direction": "expense",
        },
    ]
