import importlib
import os
import tempfile
import unittest
from datetime import datetime
from unittest.mock import Mock, patch

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
        from app.models.bank import BankProvider

        BankProvider.metadata.drop_all(bind=self.engine)
        BankProvider.metadata.create_all(bind=self.engine)
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

    def connect_mock_provider(self, headers, provider_code="VPBANK_MOCK", scopes=None):
        initiated = self.client.post(
            "/api/open-banking/connect/initiate",
            headers=headers,
            json={"provider_code": provider_code},
        )
        self.assertEqual(initiated.status_code, 200)
        selected_account_ids = [
            account["external_account_id"]
            for account in initiated.json()["available_accounts"]
        ]
        authorized = self.client.post(
            "/api/open-banking/connect/authorize",
            headers=headers,
            json={
                "provider_code": provider_code,
                "username": "demo",
                "otp_code": "123456",
                "scopes": scopes or ["accounts:read", "balances:read", "transactions:read"],
                "selected_account_ids": selected_account_ids,
            },
        )
        self.assertEqual(authorized.status_code, 200)
        return authorized.json()["connection"]

    def test_protected_routes_reject_missing_token(self):
        response = self.client.get("/api/accounts")

        self.assertIn(response.status_code, (401, 403))

    def test_demo_login_connect_sync_and_consents(self):
        headers = self.auth_headers()

        providers = self.client.get("/api/open-banking/providers", headers=headers)
        self.assertEqual(providers.status_code, 200)
        self.assertGreaterEqual(len(providers.json()), 3)

        connected = self.connect_mock_provider(headers)
        self.assertEqual(connected["status"], "connected")

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

    def test_connection_requires_authorization_and_rejects_wrong_otp(self):
        headers = self.auth_headers()
        initiated = self.client.post(
            "/api/open-banking/connect/initiate",
            headers=headers,
            json={"provider_code": "VPBANK_MOCK"},
        )
        self.assertEqual(initiated.status_code, 200)
        self.assertEqual(initiated.json()["connection"]["status"], "pending_authorization")
        self.assertEqual(self.client.get("/api/consents", headers=headers).json(), [])

        selected_account_ids = [
            account["external_account_id"]
            for account in initiated.json()["available_accounts"]
        ]
        rejected = self.client.post(
            "/api/open-banking/connect/authorize",
            headers=headers,
            json={
                "provider_code": "VPBANK_MOCK",
                "username": "demo",
                "otp_code": "000000",
                "scopes": ["accounts:read", "balances:read", "transactions:read"],
                "selected_account_ids": selected_account_ids,
            },
        )
        self.assertEqual(rejected.status_code, 401)
        self.assertIn("Invalid OTP", rejected.json()["detail"])
        connection = self.client.get("/api/open-banking/connections", headers=headers).json()[0]
        self.assertEqual(connection["status"], "pending_authorization")
        blocked_sync = self.client.post(
            "/api/open-banking/sync",
            headers=headers,
            json={"provider_code": "VPBANK_MOCK"},
        )
        self.assertEqual(blocked_sync.status_code, 409)

    def test_mock_connection_accepts_a_fake_customer_identifier(self):
        headers = self.auth_headers()
        initiated = self.client.post(
            "/api/open-banking/connect/initiate",
            headers=headers,
            json={"provider_code": "VPBANK_MOCK"},
        )
        selected_account_ids = [
            account["external_account_id"]
            for account in initiated.json()["available_accounts"]
        ]
        authorized = self.client.post(
            "/api/open-banking/connect/authorize",
            headers=headers,
            json={
                "provider_code": "VPBANK_MOCK",
                "username": "HOANG THUY LINH",
                "account_number": "0345678910",
                "otp_code": "123456",
                "scopes": ["accounts:read", "balances:read", "transactions:read"],
                "selected_account_ids": selected_account_ids,
            },
        )
        self.assertEqual(authorized.status_code, 200)
        self.assertEqual(authorized.json()["connection"]["status"], "connected")

    def test_budgets_insights_and_chat_are_user_scoped(self):
        headers = self.auth_headers()
        self.connect_mock_provider(headers)
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
        self.assertIn("chi tiêu", chat.json()["answer"])
        self.assertEqual(chat.json()["provider"], "rule_based")
        self.assertTrue(chat.json()["context_used"])

        history = self.client.get("/api/ai/chat/history", headers=headers)
        self.assertEqual(history.status_code, 200)
        self.assertEqual([item["role"] for item in history.json()], ["user", "assistant"])

    def test_ai_chat_calls_selected_provider_with_summarized_user_context(self):
        headers = self.auth_headers()
        self.connect_mock_provider(headers)
        self.client.post("/api/open-banking/sync", headers=headers, json={"provider_code": "VPBANK_MOCK"})

        import app.services.ai_coach_service as coach_service

        provider = Mock(provider_name="test_provider")
        provider.generate_answer.return_value = "Câu trả lời từ AI."
        with patch.object(coach_service, "get_ai_provider", return_value=provider):
            chat = self.client.post(
                "/api/ai/chat",
                headers=headers,
                json={"message": "Tháng này tôi tiêu nhiều nhất vào đâu?"},
            )

        self.assertEqual(chat.status_code, 200)
        self.assertEqual(chat.json()["answer"], "Câu trả lời từ AI.")
        self.assertEqual(chat.json()["provider"], "test_provider")
        self.assertTrue(chat.json()["context_used"])
        context = provider.generate_answer.call_args.kwargs["financial_context"]
        self.assertIn("total_balance", context)
        self.assertIn("top_categories", context)
        self.assertIn("recent_transactions", context)
        self.assertIn("connected_providers", context)
        self.assertNotIn("hashed_password", context)
        self.assertNotIn("token", context)

    def test_ai_provider_registry_falls_back_to_rule_based(self):
        import app.integrations.ai.registry as registry
        from app.integrations.ai.rule_based_provider import RuleBasedAIProvider
        from app.integrations.ai.openai_provider import OpenAIAIProvider

        with patch.object(registry.settings, "ai_provider", "unknown"):
            self.assertIsInstance(registry.get_ai_provider(), RuleBasedAIProvider)
        with patch.object(registry.settings, "ai_provider", "openai"):
            self.assertIsInstance(registry.get_ai_provider(), OpenAIAIProvider)

    def test_openai_provider_handles_missing_key(self):
        from app.core.config import settings
        from app.integrations.ai.openai_provider import OpenAIAIProvider

        with patch.object(settings, "openai_api_key", None):
            answer = OpenAIAIProvider().generate_answer("test", {})
        self.assertEqual(answer, "AI provider is not configured yet.")

    def test_rule_based_provider_answers_balance_question_directly(self):
        from app.integrations.ai.rule_based_provider import RuleBasedAIProvider

        answer = RuleBasedAIProvider().generate_answer(
            "cho tôi biết số dư hiện tại",
            {
                "synced_data_available": True,
                "total_balance": {"VND": 54423000},
                "monthly_income": {"VND": 0},
                "monthly_expense": {"VND": 30000},
                "recurring_merchants": [{"merchant": "Netflix", "occurrences": 4}],
            },
        )
        self.assertEqual(answer, "Số dư hiện tại của bạn là 54,423,000 VND.")

    def test_ollama_provider_handles_unavailable_service(self):
        import httpx
        import app.integrations.ai.ollama_provider as ollama_provider

        with patch.object(ollama_provider.httpx, "post", side_effect=httpx.ConnectError("offline")):
            answer = ollama_provider.OllamaAIProvider().generate_answer("test", {})
        self.assertEqual(answer, "Ollama provider is currently unavailable.")

    def test_mock_bank_webhook_uses_provider_adapter(self):
        headers = self.auth_headers()
        self.connect_mock_provider(headers)
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

    def test_mock_bank_deposit_and_withdraw_update_balance(self):
        accounts = self.client.get("/api/mock-bank/accounts?provider_code=VPBANK_MOCK").json()
        account = accounts[0]

        deposited = self.client.post(
            "/api/mock-bank/deposit",
            json={
                "provider_code": "VPBANK_MOCK",
                "external_account_id": account["external_account_id"],
                "amount": 500000,
            },
        )
        self.assertEqual(deposited.status_code, 200)
        self.assertEqual(deposited.json()["direction"], "income")
        self.assertEqual(deposited.json()["amount"], 500000)
        self.assertEqual(deposited.json()["balance_after"], account["balance"] + 500000)

        withdrawn = self.client.post(
            "/api/mock-bank/withdraw",
            json={
                "provider_code": "VPBANK_MOCK",
                "external_account_id": account["external_account_id"],
                "amount": 200000,
            },
        )
        self.assertEqual(withdrawn.status_code, 200)
        self.assertEqual(withdrawn.json()["direction"], "expense")
        self.assertEqual(withdrawn.json()["amount"], -200000)
        self.assertEqual(withdrawn.json()["balance_after"], deposited.json()["balance_after"] - 200000)

        overdraft = self.client.post(
            "/api/mock-bank/withdraw",
            json={
                "provider_code": "VPBANK_MOCK",
                "external_account_id": account["external_account_id"],
                "amount": withdrawn.json()["balance_after"] + 1,
            },
        )
        self.assertEqual(overdraft.status_code, 422)

    def test_mock_bank_transfer_creates_recipient_transaction(self):
        accounts = self.client.get("/api/mock-bank/accounts?provider_code=VPBANK_MOCK").json()
        account = accounts[0]

        transferred = self.client.post(
            "/api/mock-bank/transfer",
            json={
                "provider_code": "VPBANK_MOCK",
                "external_account_id": account["external_account_id"],
                "recipient_bank_name": "Techcombank",
                "recipient_account_number": "19031234567890",
                "recipient_account_name": "Nguyen Van A",
                "amount": 750000,
                "note": "Dinner split",
            },
        )
        self.assertEqual(transferred.status_code, 200)
        body = transferred.json()
        self.assertEqual(body["direction"], "expense")
        self.assertEqual(body["amount"], -750000)
        self.assertEqual(body["category"], "transfer")
        self.assertEqual(body["description"], "Dinner split")
        self.assertEqual(body["merchant_name"], "Nguyen Van A - Techcombank")
        self.assertEqual(body["recipient_bank_name"], "Techcombank")
        self.assertEqual(body["recipient_account_number"], "19031234567890")
        self.assertEqual(body["recipient_account_name"], "Nguyen Van A")
        self.assertEqual(body["balance_after"], account["balance"] - 750000)

        overdraft = self.client.post(
            "/api/mock-bank/transfer",
            json={
                "provider_code": "VPBANK_MOCK",
                "external_account_id": account["external_account_id"],
                "recipient_bank_name": "Techcombank",
                "recipient_account_number": "19031234567890",
                "recipient_account_name": "Nguyen Van A",
                "amount": body["balance_after"] + 1,
            },
        )
        self.assertEqual(overdraft.status_code, 422)

    def test_mock_bank_webhook_creates_local_account_after_connect_without_sync(self):
        headers = self.auth_headers()
        self.connect_mock_provider(headers, "vpbank_mock")
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
        self.connect_mock_provider(headers)

        disconnected = self.client.post(
            "/api/open-banking/disconnect",
            headers=headers,
            json={"provider_code": "VPBANK_MOCK"},
        )
        self.assertEqual(disconnected.status_code, 200)
        self.assertEqual(disconnected.json()["status"], "disconnected")
        connections = self.client.get("/api/open-banking/connections", headers=headers)
        self.assertEqual(connections.json()[0]["status"], "revoked")
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
        self.connect_mock_provider(headers)
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
        self.connect_mock_provider(headers)
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
