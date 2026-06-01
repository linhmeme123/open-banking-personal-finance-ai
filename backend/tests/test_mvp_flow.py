import importlib
import os
import tempfile
import unittest
from datetime import datetime

from fastapi.testclient import TestClient


class MvpFlowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        cls.db_file.close()
        os.environ["DATABASE_URL"] = f"sqlite:///{cls.db_file.name}"
        os.environ["SECRET_KEY"] = "test-secret"
        os.environ["CORS_ORIGINS"] = "http://localhost:3000"

        import app.core.config as config
        import app.db.session as session
        import app.models as models
        import app.main as main

        importlib.reload(config)
        importlib.reload(session)
        importlib.reload(models)
        importlib.reload(main)

        cls.base = session.Base
        cls.engine = session.engine
        cls.client = TestClient(main.app)

    @classmethod
    def tearDownClass(cls):
        os.unlink(cls.db_file.name)

    def setUp(self):
        self.base.metadata.drop_all(bind=self.engine)
        self.base.metadata.create_all(bind=self.engine)
        from app.integrations.banking.fake_bank_store import reset_store

        reset_store()

    def auth_headers(self):
        payload = {
            "full_name": "Demo User",
            "email": f"{self._testMethodName}@example.com",
            "password": "demo-password",
        }
        response = self.client.post(
            "/api/auth/signup",
            json=payload,
        )
        if response.status_code == 400:
            response = self.client.post(
                "/api/auth/login",
                json={"email": payload["email"], "password": payload["password"]},
            )
        self.assertEqual(response.status_code, 200)
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def test_protected_routes_reject_missing_token(self):
        response = self.client.get("/api/accounts")

        self.assertIn(response.status_code, (401, 403))

    def test_demo_login_connect_sync_and_consents(self):
        headers = self.auth_headers()

        providers = self.client.get("/api/open-banking/providers", headers=headers)
        self.assertEqual(providers.status_code, 200)
        self.assertGreaterEqual(len(providers.json()), 3)

        connected = self.client.post(
            "/api/open-banking/connect",
            headers=headers,
            json={"provider_code": "VPBANK_MOCK", "scope": "accounts:read transactions:read"},
        )
        self.assertEqual(connected.status_code, 200)
        self.assertEqual(connected.json()["status"], "connected")

        connections = self.client.get("/api/open-banking/connections", headers=headers)
        self.assertEqual(connections.status_code, 200)
        self.assertEqual(connections.json()[0]["provider_code"], "VPBANK_MOCK")

        consents = self.client.get("/api/consents", headers=headers)
        self.assertEqual(consents.status_code, 200)
        self.assertEqual(consents.json()[0]["provider_code"], "VPBANK_MOCK")
        self.assertEqual(consents.json()[0]["action"], "granted")

        first_sync = self.client.post(
            "/api/open-banking/sync",
            headers=headers,
            json={"provider_code": "VPBANK_MOCK"},
        )
        self.assertEqual(first_sync.status_code, 200)
        self.assertGreater(first_sync.json()["created_transactions"], 0)

        second_sync = self.client.post(
            "/api/open-banking/sync",
            headers=headers,
            json={"provider_code": "VPBANK_MOCK"},
        )
        self.assertEqual(second_sync.status_code, 200)
        self.assertEqual(second_sync.json()["created_transactions"], 0)

        accounts = self.client.get("/api/accounts", headers=headers)
        self.assertEqual(accounts.status_code, 200)
        self.assertEqual(len(accounts.json()), 1)
        self.assertTrue(all(account["provider_code"] == "VPBANK_MOCK" for account in accounts.json()))

        transactions = self.client.get("/api/transactions?provider_code=VPBANK_MOCK&category=food", headers=headers)
        self.assertEqual(transactions.status_code, 200)
        self.assertTrue(transactions.json())
        self.assertTrue(all(tx["category"] == "food" for tx in transactions.json()))
        self.assertTrue(all(tx["provider_code"] == "VPBANK_MOCK" for tx in transactions.json()))

        categorized = self.client.post(
            "/api/transactions/categorize",
            headers=headers,
            json={"transaction_id": transactions.json()[0]["id"]},
        )
        self.assertEqual(categorized.status_code, 200)
        self.assertEqual(categorized.json()["category"], "food")

    def test_budgets_insights_and_chat_are_user_scoped(self):
        headers = self.auth_headers()
        self.client.post(
            "/api/open-banking/connect",
            headers=headers,
            json={"provider_code": "VPBANK_MOCK", "scope": "accounts:read transactions:read"},
        )
        self.client.post("/api/open-banking/sync", headers=headers, json={"provider_code": "VPBANK_MOCK"})

        budget = self.client.post(
            "/api/budgets",
            headers=headers,
            json={"category": "food", "month": datetime.utcnow().strftime("%Y-%m"), "monthly_limit": 1000000},
        )
        self.assertEqual(budget.status_code, 200)
        self.assertEqual(budget.json()["category"], "food")

        budgets = self.client.get("/api/budgets", headers=headers)
        self.assertEqual(budgets.status_code, 200)
        self.assertGreaterEqual(len(budgets.json()), 1)

        summary = self.client.get("/api/insights/monthly-summary", headers=headers)
        self.assertEqual(summary.status_code, 200)
        self.assertIn("category_breakdown", summary.json())
        self.assertIn("budget_status", summary.json())

        breakdown = self.client.get("/api/insights/category-breakdown", headers=headers)
        self.assertEqual(breakdown.status_code, 200)
        self.assertTrue(any(item["category"] == "food" for item in breakdown.json()))

        recurring = self.client.get("/api/insights/recurring-payments", headers=headers)
        self.assertEqual(recurring.status_code, 200)
        self.assertIsInstance(recurring.json(), list)

        chat = self.client.post(
            "/api/ai/chat",
            headers=headers,
            json={"message": "Tháng này tôi chi tiêu thế nào?"},
        )
        self.assertEqual(chat.status_code, 200)
        self.assertIn("tổng chi tiêu", chat.json()["answer"].lower())

        history = self.client.get("/api/ai/chat/history", headers=headers)
        self.assertEqual(history.status_code, 200)
        self.assertEqual([item["role"] for item in history.json()], ["user", "assistant"])

    def test_mock_bank_webhook_uses_provider_adapter(self):
        headers = self.auth_headers()
        self.client.post(
            "/api/open-banking/connect",
            headers=headers,
            json={"provider_code": "VPBANK_MOCK"},
        )
        self.client.post("/api/open-banking/sync", headers=headers, json={"provider_code": "VPBANK_MOCK"})
        accounts = self.client.get("/api/mock-bank/accounts?provider_code=VPBANK_MOCK").json()

        created = self.client.post(
            "/api/mock-bank/transactions",
            json={
                "provider_code": "VPBANK_MOCK",
                "external_account_id": accounts[0]["external_account_id"],
                "description": "Highlands Coffee",
                "merchant_name": "Highlands Coffee",
                "amount": 65000,
                "direction": "expense",
            },
        )
        self.assertEqual(created.status_code, 200)
        self.assertEqual(created.json()["webhook_status"], "pending")
        self.assertEqual(created.json()["sync_status"], "pending")
        self.assertEqual(created.json()["balance_after"], created.json()["balance_before"] - 65000)
        webhook = self.client.post(
            "/api/mock-bank/webhooks/send",
            headers=headers,
            json={
                "provider_code": "VPBANK_MOCK",
                "external_transaction_id": created.json()["external_transaction_id"],
            },
        )
        self.assertEqual(webhook.status_code, 200)
        self.assertEqual(webhook.json()["transactions_added"], 1)
        transactions = self.client.get(
            f"/api/mock-bank/transactions?provider_code=VPBANK_MOCK&external_account_id={accounts[0]['external_account_id']}"
        )
        synced = next(
            item
            for item in transactions.json()
            if item["external_transaction_id"] == created.json()["external_transaction_id"]
        )
        self.assertEqual(synced["webhook_status"], "delivered")
        self.assertEqual(synced["sync_status"], "synced")
        self.assertEqual(synced["category"], "food")
        events = self.client.get(
            f"/api/mock-bank/transactions/{created.json()['external_transaction_id']}/events?provider_code=VPBANK_MOCK"
        )
        self.assertEqual(events.status_code, 200)
        event_types = [event["event_type"] for event in events.json()]
        self.assertIn("webhook_sent", event_types)
        self.assertIn("webhook_verified", event_types)
        self.assertIn("transaction_synced", event_types)
        self.assertIn("transaction_categorized", event_types)

    def test_mock_bank_webhook_creates_local_account_after_connect_without_sync(self):
        headers = self.auth_headers()
        connected = self.client.post(
            "/api/open-banking/connect",
            headers=headers,
            json={"provider_code": "vpbank_mock"},
        )
        self.assertEqual(connected.status_code, 200)
        accounts = self.client.get("/api/mock-bank/accounts?provider_code=VPBANK_MOCK").json()
        source_account = accounts[0]
        created = self.client.post(
            "/api/mock-bank/transactions",
            json={
                "provider_code": "VPBANK_MOCK",
                "external_account_id": source_account["external_account_id"],
                "description": "Highlands Coffee",
                "merchant_name": "Highlands Coffee",
                "amount": 65000,
                "direction": "expense",
            },
        )
        self.assertEqual(created.status_code, 200)

        webhook = self.client.post(
            "/api/mock-bank/webhooks/send",
            headers=headers,
            json={
                "provider_code": "vpbank_mock",
                "external_transaction_id": created.json()["external_transaction_id"],
            },
        )
        self.assertEqual(webhook.status_code, 200)
        self.assertEqual(webhook.json()["transactions_added"], 1)

        transactions = self.client.get("/api/transactions", headers=headers)
        self.assertEqual(transactions.status_code, 200)
        imported = next(
            item
            for item in transactions.json()
            if item["description"] == "Highlands Coffee"
            and item["id"] == max(transaction["id"] for transaction in transactions.json())
        )
        self.assertEqual(imported["category"], "food")

        local_accounts = self.client.get("/api/accounts", headers=headers)
        self.assertEqual(local_accounts.status_code, 200)
        self.assertEqual(len(local_accounts.json()), 1)
        self.assertEqual(local_accounts.json()[0]["balance"], created.json()["balance_after"])

        duplicate = self.client.post(
            "/api/mock-bank/webhooks/send",
            headers=headers,
            json={
                "provider_code": "VPBANK_MOCK",
                "external_transaction_id": created.json()["external_transaction_id"],
            },
        )
        self.assertEqual(duplicate.status_code, 200)
        self.assertEqual(duplicate.json()["status"], "already_synced")
        self.assertEqual(duplicate.json()["transactions_added"], 0)
        duplicate_accounts = self.client.get("/api/accounts", headers=headers)
        self.assertEqual(duplicate_accounts.json()[0]["balance"], created.json()["balance_after"])

    def test_mock_bank_webhook_marks_failed_when_provider_is_not_connected(self):
        headers = self.auth_headers()
        accounts = self.client.get("/api/mock-bank/accounts?provider_code=VPBANK_MOCK").json()
        created = self.client.post(
            "/api/mock-bank/transactions",
            json={
                "provider_code": "VPBANK_MOCK",
                "external_account_id": accounts[0]["external_account_id"],
                "description": "Highlands Coffee",
                "amount": 65000,
                "direction": "expense",
            },
        )

        webhook = self.client.post(
            "/api/mock-bank/webhooks/send",
            headers=headers,
            json={
                "provider_code": "VPBANK_MOCK",
                "external_transaction_id": created.json()["external_transaction_id"],
            },
        )
        self.assertEqual(webhook.status_code, 409)
        transactions = self.client.get("/api/mock-bank/transactions?provider_code=VPBANK_MOCK").json()
        failed = next(
            item
            for item in transactions
            if item["external_transaction_id"] == created.json()["external_transaction_id"]
        )
        self.assertEqual(failed["webhook_status"], "failed")
        self.assertEqual(failed["sync_status"], "failed")

    def test_disconnect_provider_revokes_consent_and_blocks_future_pushes(self):
        headers = self.auth_headers()
        self.client.post(
            "/api/open-banking/connect",
            headers=headers,
            json={"provider_code": "VPBANK_MOCK"},
        )

        disconnected = self.client.post(
            "/api/open-banking/disconnect",
            headers=headers,
            json={"provider_code": "VPBANK_MOCK"},
        )
        self.assertEqual(disconnected.status_code, 200)
        self.assertEqual(disconnected.json()["status"], "disconnected")
        connections = self.client.get("/api/open-banking/connections", headers=headers)
        self.assertEqual(connections.json(), [])
        consents = self.client.get("/api/consents", headers=headers)
        self.assertEqual(consents.json()[0]["action"], "revoked")

        accounts = self.client.get("/api/mock-bank/accounts?provider_code=VPBANK_MOCK").json()
        created = self.client.post(
            "/api/mock-bank/transactions",
            json={
                "provider_code": "VPBANK_MOCK",
                "external_account_id": accounts[0]["external_account_id"],
                "description": "Đạp xe hồ Tây",
                "amount": 30000,
                "direction": "expense",
            },
        )
        webhook = self.client.post(
            "/api/mock-bank/webhooks/send",
            headers=headers,
            json={
                "provider_code": "VPBANK_MOCK",
                "external_transaction_id": created.json()["external_transaction_id"],
            },
        )
        self.assertEqual(webhook.status_code, 409)

    def test_mock_bank_cycling_transaction_is_visible_as_transport_after_push(self):
        headers = self.auth_headers()
        self.client.post(
            "/api/open-banking/connect",
            headers=headers,
            json={"provider_code": "VPBANK_MOCK"},
        )
        accounts = self.client.get("/api/mock-bank/accounts?provider_code=VPBANK_MOCK").json()
        created = self.client.post(
            "/api/mock-bank/transactions",
            json={
                "provider_code": "VPBANK_MOCK",
                "external_account_id": accounts[0]["external_account_id"],
                "description": "Đạp xe hồ Tây",
                "merchant_name": "Đạp xe",
                "amount": 30000,
                "direction": "expense",
            },
        )

        webhook = self.client.post(
            "/api/mock-bank/webhooks/send",
            headers=headers,
            json={
                "provider_code": "VPBANK_MOCK",
                "external_transaction_id": created.json()["external_transaction_id"],
            },
        )
        self.assertEqual(webhook.status_code, 200)

        transactions = self.client.get("/api/transactions?search=Đạp xe", headers=headers)
        self.assertEqual(transactions.status_code, 200)
        self.assertEqual(len(transactions.json()), 1)
        self.assertEqual(transactions.json()[0]["external_id"], created.json()["external_transaction_id"])
        self.assertEqual(transactions.json()[0]["description"], "Đạp xe hồ Tây")
        self.assertEqual(transactions.json()[0]["category"], "transport")

    def test_bank_transaction_webhook_route_normalizes_json_payload(self):
        headers = self.auth_headers()
        self.client.post(
            "/api/open-banking/connect",
            headers=headers,
            json={"provider_code": "VPBANK_MOCK"},
        )
        accounts = self.client.get("/api/mock-bank/accounts?provider_code=VPBANK_MOCK").json()
        created = self.client.post(
            "/api/mock-bank/transactions",
            json={
                "provider_code": "VPBANK_MOCK",
                "external_account_id": accounts[0]["external_account_id"],
                "description": "Highlands Coffee",
                "merchant_name": "Highlands Coffee",
                "amount": 65000,
                "direction": "expense",
            },
        )

        webhook = self.client.post(
            "/api/webhooks/bank/transactions",
            headers={"x-fake-bank-signature": "velora-fake-bank"},
            json={"provider_code": "VPBANK_MOCK", "transaction": created.json()},
        )
        self.assertEqual(webhook.status_code, 200)
        transactions = self.client.get("/api/transactions", headers=headers)
        self.assertEqual(transactions.status_code, 200)
        self.assertEqual(transactions.json()[0]["category"], "food")

    def test_public_sandbox_is_not_exposed_as_mock_console(self):
        response = self.client.get("/api/mock-bank/accounts?provider_code=OPEN_BANK_PROJECT_SANDBOX")

        self.assertEqual(response.status_code, 409)


if __name__ == "__main__":
    unittest.main()
