from datetime import datetime, timedelta
from decimal import Decimal
from random import choice
from uuid import uuid4


ACCOUNTS: dict[str, list[dict]] = {}
TRANSACTIONS: dict[str, list[dict]] = {}

TEMPLATES = [
    ("Highlands Coffee", "Highlands Coffee", Decimal("-65000"), "expense"),
    ("Grab Bike", "Grab", Decimal("-42000"), "expense"),
    ("Salary Payroll", "Company Payroll", Decimal("12000000"), "income"),
    ("Shopee order", "Shopee", Decimal("-350000"), "expense"),
    ("Internet bill", "VNPT Internet", Decimal("-220000"), "expense"),
]


def reset_store() -> None:
    ACCOUNTS.clear()
    TRANSACTIONS.clear()


def _seed(provider_code: str) -> None:
    if provider_code in ACCOUNTS:
        return
    account_id = f"{provider_code.lower()}-checking"
    ACCOUNTS[provider_code] = [
        {
            "external_account_id": account_id,
            "account_name": f"{provider_code} Everyday Account",
            "account_type": "checking",
            "currency": "VND",
            "balance": Decimal("18450000"),
        }
    ]
    TRANSACTIONS[provider_code] = []
    for offset, template in enumerate(TEMPLATES, start=1):
        create_transaction(provider_code, account_id, *template, transaction_time=datetime.utcnow() - timedelta(days=offset))


def list_accounts(provider_code: str) -> list[dict]:
    _seed(provider_code)
    return ACCOUNTS[provider_code]


def create_account(provider_code: str, account_name: str, account_type: str, currency: str, balance: Decimal) -> dict:
    _seed(provider_code)
    account = {
        "external_account_id": f"{provider_code.lower()}-{uuid4().hex[:10]}",
        "account_name": account_name,
        "account_type": account_type,
        "currency": currency,
        "balance": balance,
    }
    ACCOUNTS[provider_code].append(account)
    return account


def list_transactions(provider_code: str, external_account_id: str | None = None) -> list[dict]:
    _seed(provider_code)
    items = TRANSACTIONS[provider_code]
    return [item for item in items if not external_account_id or item["external_account_id"] == external_account_id]


def create_transaction(
    provider_code: str,
    external_account_id: str,
    description: str,
    merchant_name: str | None,
    amount: Decimal,
    direction: str,
    transaction_time: datetime | None = None,
) -> dict:
    _seed(provider_code) if provider_code not in ACCOUNTS else None
    transaction = {
        "external_transaction_id": f"{provider_code.lower()}-{uuid4().hex}",
        "external_account_id": external_account_id,
        "transaction_time": transaction_time or datetime.utcnow(),
        "description": description,
        "merchant_name": merchant_name,
        "amount": amount,
        "currency": "VND",
        "direction": direction,
    }
    TRANSACTIONS.setdefault(provider_code, []).append(transaction)
    for account in ACCOUNTS[provider_code]:
        if account["external_account_id"] == external_account_id:
            account["balance"] += amount
            break
    return transaction


def generate_transaction(provider_code: str, external_account_id: str) -> dict:
    return create_transaction(provider_code, external_account_id, *choice(TEMPLATES))


def get_transaction(provider_code: str, external_transaction_id: str) -> dict | None:
    return next(
        (
            item
            for item in list_transactions(provider_code)
            if item["external_transaction_id"] == external_transaction_id
        ),
        None,
    )
