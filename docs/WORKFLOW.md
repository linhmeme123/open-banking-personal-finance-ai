# Project Workflow

## Phase 0: Product Scope

Tên dự án: Open Banking Personal Finance AI

User story chính:

> Là người dùng ngân hàng số, tôi muốn kết nối tài khoản ngân hàng của mình, cấp quyền truy cập dữ liệu, xem dòng tiền, quản lý ngân sách, nhận insight chi tiêu, và hỏi AI để nhận gợi ý tài chính cá nhân dựa trên dữ liệu của tôi.

Mục tiêu portfolio:

- Thể hiện hiểu biết về Open Banking, consent, account aggregation, transaction analytics, và AI finance assistant.
- Có flow demo end-to-end thay vì chỉ mock UI.
- Giữ an toàn: dùng sandbox provider, demo auth, không kết nối ngân hàng thật, không lưu credential thật.

## Phase 1: Target User Journey

1. User mở app và đăng nhập bằng demo identity.
2. User chọn sandbox provider: `BANK_A`, `BANK_B`, hoặc `EWALLET_X`.
3. User cấp consent với scope `accounts:read transactions:read`.
4. Backend lưu consent event có hash audit.
5. User sync dữ liệu account/transaction từ sandbox provider.
6. Backend chuẩn hóa transaction, phân loại category, và lưu vào PostgreSQL.
7. User xem accounts, transactions, dashboard, insights, budgets, recurring payments.
8. User hỏi AI coach; câu trả lời dựa trên transaction, budget, category, và recurring data đã lưu.
9. User xem consent audit trail để chứng minh banking relevance và privacy mindset.

## Phase 2: Architecture

```txt
Next.js Frontend
  - Home / demo sign-in
  - Connect bank
  - Accounts
  - Dashboard
  - Transactions
  - Budgets
  - Insights
  - Consent audit
  - AI Coach
        |
        | REST + Bearer demo token
        v
FastAPI Backend
  - Auth-lite dependency
  - API routers
  - Service layer
  - Open Banking sandbox adapter
  - Rule-based categorizer
  - Data-grounded AI coach
        |
        | SQLAlchemy
        v
PostgreSQL
```

## Phase 3: Domain Model

Core entities:

- `User`: demo identity and owner of finance data.
- `BankProvider`: sandbox provider registry.
- `BankConnection`: user-provider connection status, consent scope, last sync timestamp.
- `Account`: normalized bank account.
- `Transaction`: normalized transaction with AI category and confidence.
- `Category`: category dictionary for future expansion.
- `Budget`: monthly category limit.
- `ConsentEvent`: audit event for granted/revoked consent, including hash.
- `AiChatMessage`: persisted user/assistant chat history.

## Phase 4: API Design

### Auth

- `POST /api/auth/demo-login`

### Account

- `GET /api/accounts`
- `GET /api/accounts/{account_id}`

### Transaction

- `GET /api/transactions`
- `GET /api/transactions?month=2026-05`
- `GET /api/transactions?category=food_drink`
- `GET /api/transactions?month=2026-05&category=food_drink`

### Open Banking

- `GET /api/open-banking/providers`
- `POST /api/open-banking/connect`
- `POST /api/open-banking/sync`

### Budget

- `GET /api/budgets`
- `POST /api/budgets`

### AI

- `POST /api/ai/categorize`
- `POST /api/ai/chat`
- `GET /api/ai/chat/history`

### Insights

- `GET /api/insights/monthly-summary`
- `GET /api/insights/category-breakdown`
- `GET /api/insights/recurring-payments`

### Consent

- `POST /api/consents`
- `GET /api/consents`

## Phase 5: Development Order

1. Backend health check.
2. Auth-lite demo identity and current-user dependency.
3. Database models for banking connection, account, transaction, budget, consent, AI chat.
4. Open Banking sandbox providers.
5. Consent grant and audit hash.
6. Idempotent sync for accounts and transactions.
7. Transaction category rules and confidence.
8. Account and transaction APIs with filters.
9. Budget APIs.
10. Insight APIs: monthly summary, category breakdown, recurring payments, budget status.
11. AI coach response grounded in stored user data.
12. Chat history persistence.
13. Frontend sign-in and connect bank flow.
14. Frontend accounts, transactions, dashboard, budget, insight, consent, chat pages.
15. Backend flow tests.
16. Frontend production build.
17. Docker Compose verification.
18. README polish, architecture diagram, ERD, screenshots, and demo video.

## Phase 6: Testing Checklist

Backend:

- Demo login returns a bearer token.
- Protected endpoints reject missing token.
- Provider list returns sandbox banks.
- Provider connect creates a bank connection and consent event.
- Sync creates account and transactions.
- Repeated sync is idempotent.
- Transactions filter by month and category.
- Budgets can be created and listed.
- Monthly summary includes income, expense, net cashflow, category breakdown, and budget status.
- Recurring payment detection returns repeated merchants.
- AI chat persists user and assistant messages.

Frontend:

- App builds with `npm run build`.
- Demo sign-in stores token.
- Connect page can grant consent and sync.
- Dashboard shows synced finance data.
- Transactions page filters results.
- Budgets page saves category budgets.
- Insights page shows category and recurring data.
- Consents page shows audit hashes.
- Chat page persists and displays conversation.

## Phase 7: Deployment Checklist

- Use production Docker commands instead of dev reload commands.
- Set `DATABASE_URL`, `SECRET_KEY`, `CORS_ORIGINS`, and `NEXT_PUBLIC_API_BASE_URL`.
- Run backend tests before deploy.
- Run frontend build before deploy.
- Use a managed PostgreSQL database for hosted demo.
- Disable real credentials in screenshots and demo videos.

## Phase 8: Portfolio Checklist

- Architecture diagram.
- ERD.
- API docs from FastAPI `/docs`.
- Screenshots of connect flow, dashboard, transactions, AI coach, consent audit.
- Demo video 2-3 minutes.
- README sections:
  - Banking relevance.
  - Open Banking flow.
  - AI approach.
  - Security and privacy considerations.
  - Local run guide.
  - Deployment notes.

## Phase 9: Production-Hardening Backlog

- Replace demo auth with OAuth/OIDC or passwordless login.
- Add Alembic migrations instead of `Base.metadata.create_all`.
- Encrypt bank tokens if real aggregation is added.
- Add rate limiting and structured request logs.
- Add pagination for transactions and chat history.
- Add manual category correction and feedback loop.
- Replace rule-based categorizer with ML/embedding classifier.
- Replace mock AI coach with LLM function calling over finance tools.
- Add anomaly detection.
- Add consent revocation flow.
- Optionally anchor consent event hash to a blockchain testnet.
