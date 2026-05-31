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
            json={"provider_code": "TIMO", "scope": "accounts:read transactions:read"},
        )
        self.assertEqual(connected.status_code, 200)
        self.assertEqual(connected.json()["status"], "connected")

        connections = self.client.get("/api/open-banking/connections", headers=headers)
        self.assertEqual(connections.status_code, 200)
        self.assertEqual(connections.json()[0]["provider_code"], "TIMO")

        consents = self.client.get("/api/consents", headers=headers)
        self.assertEqual(consents.status_code, 200)
        self.assertEqual(consents.json()[0]["provider_code"], "TIMO")
        self.assertEqual(consents.json()[0]["action"], "granted")

        first_sync = self.client.post(
            "/api/open-banking/sync",
            headers=headers,
            json={"provider_code": "TIMO"},
        )
        self.assertEqual(first_sync.status_code, 200)
        self.assertGreater(first_sync.json()["created_transactions"], 0)

        second_sync = self.client.post(
            "/api/open-banking/sync",
            headers=headers,
            json={"provider_code": "TIMO"},
        )
        self.assertEqual(second_sync.status_code, 200)
        self.assertEqual(second_sync.json()["created_transactions"], 0)

        accounts = self.client.get("/api/accounts", headers=headers)
        self.assertEqual(accounts.status_code, 200)
        self.assertEqual(len(accounts.json()), 2)
        self.assertTrue(all(account["provider_code"] == "TIMO" for account in accounts.json()))

        transactions = self.client.get("/api/transactions?provider_code=TIMO&category=food", headers=headers)
        self.assertEqual(transactions.status_code, 200)
        self.assertTrue(transactions.json())
        self.assertTrue(all(tx["category"] == "food" for tx in transactions.json()))
        self.assertTrue(all(tx["provider_code"] == "TIMO" for tx in transactions.json()))

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
            json={"provider_code": "TIMO", "scope": "accounts:read transactions:read"},
        )
        self.client.post("/api/open-banking/sync", headers=headers, json={"provider_code": "TIMO"})

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


if __name__ == "__main__":
    unittest.main()
