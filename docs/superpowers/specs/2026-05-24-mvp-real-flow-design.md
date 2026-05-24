# MVP Real Flow Design

## Goal

Turn the starter mock into a demoable personal-finance app flow:

1. A demo user signs in.
2. The user selects a sandbox bank provider.
3. The app records consent.
4. The backend syncs accounts and transactions.
5. The user views dashboard, accounts, transactions, budgets, recurring payments, consent audit, and AI coach answers grounded in stored data.

This remains a portfolio-safe sandbox. It does not connect to real banks or store real bank credentials.

## Scope

In scope:

- Auth-lite demo identity with backend-issued token.
- User-scoped APIs instead of hard-coded `user_id=1`.
- Bank connection records for sandbox providers.
- Consent events tied to connection actions.
- Idempotent account and transaction sync.
- Transaction month/category filters.
- Budget model and API.
- Insights for monthly summary, category breakdown, and recurring payments.
- Chat history persistence and data-grounded coach response.
- Frontend pages for sign-in, connect bank, dashboard, accounts, transactions, budgets, insights, consent audit, and chat.
- Stronger `docs/WORKFLOW.md`.
- Backend tests for the critical flow.

Out of scope for this pass:

- Real bank APIs.
- Real OAuth/OpenID Connect.
- Payment initiation.
- Production secret storage.
- Real LLM API calls.
- Alembic migration setup. The app may keep `create_all` for this portfolio MVP, while workflow docs call out Alembic as the next production-hardening step.

## Architecture

The app keeps the current split:

- `frontend`: Next.js app using REST API helpers.
- `backend`: FastAPI controllers, SQLAlchemy models, service layer, and AI helpers.
- `db`: PostgreSQL in Docker Compose.

The MVP adds a thin auth dependency in the backend. Frontend requests carry a demo token after sign-in. Backend routes resolve the current user from that token and scope account, transaction, consent, budget, insight, and chat queries to that user.

## Backend Design

### Auth-lite

Add `/api/auth/demo-login`. It finds or creates the demo user and returns:

- `access_token`
- `token_type`
- `user`

The token is signed with HMAC using `SECRET_KEY`. It is intentionally simple and portfolio-friendly, but avoids hard-coded user IDs in app code.

### Domain

Add:

- `BankConnection`: user, provider, status, consent scope, last sync time.
- `Budget`: user, category, monthly limit, month.

Keep existing:

- `User`
- `BankProvider`
- `Account`
- `Transaction`
- `Category`
- `ConsentEvent`
- `AiChatMessage`

### Open Banking Flow

`GET /api/open-banking/providers` returns sandbox providers.

`POST /api/open-banking/connect`:

- Requires current user.
- Accepts provider code and scope.
- Creates or updates a bank connection.
- Writes a granted consent event.

`POST /api/open-banking/sync`:

- Requires current user.
- Accepts optional provider code.
- Ensures provider, connection, and account exist.
- Pulls provider-specific sandbox transactions.
- Categorizes new transactions.
- Skips existing transactions by `external_id`.
- Updates account balance and connection sync timestamp.

### Finance APIs

Accounts:

- `GET /api/accounts`
- `GET /api/accounts/{account_id}`

Transactions:

- `GET /api/transactions`
- `GET /api/transactions?month=YYYY-MM`
- `GET /api/transactions?category=food_drink`

Budgets:

- `GET /api/budgets`
- `POST /api/budgets`

Insights:

- `GET /api/insights/monthly-summary`
- `GET /api/insights/category-breakdown`
- `GET /api/insights/recurring-payments`

Consent:

- `GET /api/consents`
- `POST /api/consents`

AI:

- `POST /api/ai/categorize`
- `POST /api/ai/chat`
- `GET /api/ai/chat/history`

## Frontend Design

The first screen should be the usable product, not a marketing page.

Pages:

- `/`: Redirect-like product home that shows sign-in/connect status and primary actions.
- `/connect`: Provider list, consent scope, connect and sync buttons.
- `/dashboard`: Cashflow cards, category breakdown, budget status, recurring payments.
- `/accounts`: Connected accounts and balances.
- `/transactions`: Filterable transaction table.
- `/budgets`: Budget list and simple create form.
- `/insights`: Monthly summary, category breakdown, recurring payments.
- `/consents`: Consent audit trail.
- `/chat`: AI coach with persisted history.

Use simple `localStorage` token persistence for the demo.

## Error Handling

- Missing or invalid token returns `401`.
- Unknown provider returns `404`.
- User accessing another user's account returns `404`.
- Duplicate sync returns `created_transactions: 0` instead of duplicating data.
- Frontend shows useful empty states and action buttons, especially before sync.

## Testing

Backend tests cover:

- Demo login returns a token.
- Protected routes reject missing token.
- Connect provider creates consent.
- Sync creates account and transactions.
- Sync is idempotent.
- Transaction filters work.
- Insights return monthly summary, category breakdown, recurring payments.
- Budget create/list works.
- Chat persists user and assistant messages.

Frontend verification covers:

- `npm run build`.
- Browser smoke check on the main user flow if the dev server runs locally.

## Workflow Document Update

`docs/WORKFLOW.md` should become the canonical build plan:

- product goal
- user journey
- architecture
- data model
- API map
- frontend pages
- development phases
- testing checklist
- deployment checklist
- portfolio checklist
- production-hardening backlog

