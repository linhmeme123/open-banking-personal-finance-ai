# Project Workflow

## Phase 0: Scope

Tên dự án: Open Banking Personal Finance AI

User story chính:

> Là người dùng ngân hàng số, tôi muốn kết nối tài khoản ngân hàng của mình, xem dòng tiền, hiểu thói quen chi tiêu, và hỏi AI để nhận gợi ý quản lý tài chính cá nhân.

## Phase 1: Domain Model

Entity chính:

- User
- BankProvider
- Account
- Transaction
- Category
- Budget
- ConsentEvent
- AiChatMessage

## Phase 2: API Design

### Account
- `GET /api/accounts`
- `GET /api/accounts/{account_id}`

### Transaction
- `GET /api/transactions`
- `GET /api/transactions?month=2026-05`
- `GET /api/transactions?category=food`

### Open Banking
- `POST /api/open-banking/sync`
- `GET /api/open-banking/providers`

### AI
- `POST /api/ai/categorize`
- `POST /api/ai/chat`

### Insights
- `GET /api/insights/monthly-summary`
- `GET /api/insights/category-breakdown`
- `GET /api/insights/recurring-payments`

### Consent
- `POST /api/consents`
- `GET /api/consents`

## Phase 3: Development Order

1. Backend health check.
2. Database models.
3. Seed demo user/accounts/transactions.
4. Transactions API.
5. Frontend dashboard.
6. AI categorization.
7. Insights API.
8. AI chat.
9. Consent audit.
10. Deployment + README polish.

## Phase 4: Portfolio Checklist

- Có architecture diagram.
- Có ERD.
- Có demo video 2-3 phút.
- Có API docs.
- Có screenshots.
- Có phần “Banking relevance”.
- Có phần “AI approach”.
- Có phần “Security & privacy considerations”.
