from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4


ACCOUNTS: dict[str, list[dict]] = {}
TRANSACTIONS: dict[str, list[dict]] = {}
EVENTS: dict[str, list[dict]] = {}

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
    EVENTS.clear()


def _add_event(external_transaction_id: str, event_type: str, message: str) -> None:
    EVENTS.setdefault(external_transaction_id, []).append(
        {
            "event_type": event_type,
            "message": message,
            "created_at": datetime.utcnow(),
        }
    )


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
            "last_updated_at": datetime.utcnow(),
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
        "last_updated_at": datetime.utcnow(),
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
    category: str | None = None,
    transaction_time: datetime | None = None,
    recipient_bank_name: str | None = None,
    recipient_account_number: str | None = None,
    recipient_account_name: str | None = None,
    transfer_type: str | None = None,
) -> dict:
    _seed(provider_code) if provider_code not in ACCOUNTS else None
    reconciled_amount = abs(amount) if direction == "income" else -abs(amount)
    transaction = {
        "external_transaction_id": f"{provider_code.lower()}-{uuid4().hex}",
        "external_account_id": external_account_id,
        "transaction_time": transaction_time or datetime.utcnow(),
        "description": description,
        "merchant_name": merchant_name,
        "amount": reconciled_amount,
        "currency": "VND",
        "direction": direction,
        "category": category,
        "balance_before": None,
        "balance_after": None,
        "webhook_status": "pending",
        "sync_status": "pending",
    }
    if recipient_bank_name or recipient_account_number or recipient_account_name:
        transaction.update(
            {
                "recipient_bank_name": recipient_bank_name,
                "recipient_account_number": recipient_account_number,
                "recipient_account_name": recipient_account_name,
                "transfer_type": transfer_type,
            }
        )
    for account in ACCOUNTS[provider_code]:
        if account["external_account_id"] == external_account_id:
            transaction["balance_before"] = account["balance"]
            account["balance"] += reconciled_amount
            account["last_updated_at"] = datetime.utcnow()
            transaction["balance_after"] = account["balance"]
            break
    else:
        raise ValueError("Mock account not found")
    TRANSACTIONS.setdefault(provider_code, []).append(transaction)
    _add_event(transaction["external_transaction_id"], "transaction_created", "Transaction Created")
    _add_event(
        transaction["external_transaction_id"],
        "balance_updated",
        f"Balance Updated: {transaction['balance_before']} -> {transaction['balance_after']} {transaction['currency']}",
    )
    return transaction


def get_transaction(provider_code: str, external_transaction_id: str) -> dict | None:
    return next(
        (
            item
            for item in list_transactions(provider_code)
            if item["external_transaction_id"] == external_transaction_id
        ),
        None,
    )


def list_transaction_events(provider_code: str, external_transaction_id: str) -> list[dict]:
    if not get_transaction(provider_code, external_transaction_id):
        return []
    return EVENTS.get(external_transaction_id, [])


def mark_webhook_sent(provider_code: str, external_transaction_id: str) -> None:
    transaction = get_transaction(provider_code, external_transaction_id)
    if transaction:
        _add_event(external_transaction_id, "webhook_sent", "Webhook Sent")


def mark_webhook_verified(provider_code: str, external_transaction_id: str) -> None:
    transaction = get_transaction(provider_code, external_transaction_id)
    if transaction:
        transaction["webhook_status"] = "delivered"
        _add_event(external_transaction_id, "webhook_verified", "Webhook Verified")


def mark_transaction_synced(provider_code: str, external_transaction_id: str, category: str | None = None) -> None:
    transaction = get_transaction(provider_code, external_transaction_id)
    if not transaction:
        return
    transaction["sync_status"] = "synced"
    if category:
        transaction["category"] = category
    _add_event(external_transaction_id, "transaction_synced", "Transaction Synced")
    if category:
        _add_event(external_transaction_id, "transaction_categorized", f"Categorized as {category}")


def record_balance_updated(
    provider_code: str,
    external_transaction_id: str,
    balance_before: Decimal,
    balance_after: Decimal,
    currency: str,
) -> None:
    transaction = get_transaction(provider_code, external_transaction_id)
    if transaction:
        _add_event(
            external_transaction_id,
            "balance_updated",
            f"Balance Updated: {balance_before} -> {balance_after} {currency}",
        )


def mark_transaction_failed(provider_code: str, external_transaction_id: str, reason: str) -> None:
    transaction = get_transaction(provider_code, external_transaction_id)
    if transaction:
        transaction["webhook_status"] = "failed"
        transaction["sync_status"] = "failed"
        _add_event(external_transaction_id, "transaction_failed", f"Failed with reason: {reason}")
