# MVP Real Flow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the MVP-first real banking demo flow from sign-in through provider connect, consent, sync, finance insights, budgets, and AI coach.

**Architecture:** Keep the current FastAPI + SQLAlchemy + Next.js architecture. Add a lightweight backend auth dependency, user-scoped service APIs, sandbox bank connection state, and frontend pages that drive the full flow through real API calls.

**Tech Stack:** FastAPI, SQLAlchemy, Pydantic, PostgreSQL, Next.js App Router, React, Tailwind CSS, Docker Compose.

---

## File Map

- Modify `backend/app/core/config.py`: add `secret_key`.
- Create `backend/app/core/security.py`: HMAC demo token helpers.
- Create `backend/app/api/auth.py`: demo login endpoint.
- Modify `backend/app/main.py`: include auth router and keep table creation for MVP.
- Modify `backend/app/models/domain.py`: add `BankConnection`, `Budget`, relationships.
- Modify `backend/app/schemas/dto.py`: add request/response schemas.
- Modify `backend/app/api/accounts.py`: current-user scoped list/detail.
- Modify `backend/app/api/transactions.py`: current-user scoped filters.
- Modify `backend/app/api/open_banking.py`: connect and user-scoped sync.
- Modify `backend/app/api/insights.py`: add all workflow insight endpoints.
- Modify `backend/app/api/consents.py`: current-user scoped consent API.
- Modify `backend/app/api/ai.py`: current-user scoped chat, history, categorization ownership checks.
- Modify `backend/app/services/open_banking_mock.py`: provider-specific account/transaction fixture data.
- Modify `backend/app/services/insight_service.py`: monthly summary, category breakdown, recurring payments.
- Modify `backend/app/ai/coach.py`: persist messages and answer from user data.
- Create `backend/app/api/budgets.py`: budget list/create endpoints.
- Create `backend/tests/test_mvp_flow.py`: backend flow tests.
- Modify `frontend/lib/api.ts`: auth token handling.
- Create `frontend/lib/session.ts`: client session helpers.
- Modify `frontend/components/Nav.tsx`: add product navigation.
- Modify `frontend/app/page.tsx`: product home/sign-in gateway.
- Create `frontend/app/connect/page.tsx`: connect/sync flow.
- Create `frontend/app/accounts/page.tsx`: accounts page.
- Modify `frontend/app/dashboard/page.tsx`: real summary, budgets, recurring payments.
- Modify `frontend/app/transactions/page.tsx`: filters and empty state.
- Create `frontend/app/budgets/page.tsx`: budget management.
- Create `frontend/app/insights/page.tsx`: insight views.
- Create `frontend/app/consents/page.tsx`: consent audit trail.
- Modify `frontend/app/chat/page.tsx`: authenticated chat with history.
- Modify `docs/WORKFLOW.md`: complete workflow.

## Tasks

### Task 1: Backend flow tests

- [ ] Add `backend/tests/test_mvp_flow.py` with tests for login, protected routes, provider connect, consent creation, idempotent sync, filters, budgets, insights, and chat persistence.
- [ ] Run `cd backend && python -m pytest tests/test_mvp_flow.py -q`.
- [ ] Confirm tests fail because auth/budget/connect endpoints do not exist yet.

### Task 2: Auth-lite and domain models

- [ ] Add HMAC token helpers in `backend/app/core/security.py`.
- [ ] Add `secret_key` setting.
- [ ] Add `BankConnection` and `Budget` models.
- [ ] Add schemas for auth, provider connect, budget, insights, chat history.
- [ ] Add `/api/auth/demo-login` and current-user dependency.
- [ ] Run backend tests and confirm auth tests pass while downstream flow tests still fail.

### Task 3: Banking flow APIs

- [ ] Implement current-user scoped accounts.
- [ ] Implement provider connect with consent event creation.
- [ ] Implement provider-specific idempotent sync.
- [ ] Implement transaction filters by month and category.
- [ ] Run backend tests and confirm banking flow tests pass.

### Task 4: Budgets, insights, and AI persistence

- [ ] Implement budget list/create API.
- [ ] Implement category breakdown and recurring payments.
- [ ] Persist AI chat messages.
- [ ] Ground coach answers in transaction, category, budget, and recurring data.
- [ ] Run backend tests and confirm all backend flow tests pass.

### Task 5: Frontend real flow

- [ ] Add token-aware API helpers.
- [ ] Add sign-in/product home.
- [ ] Add connect bank page.
- [ ] Add accounts, budgets, insights, consent pages.
- [ ] Upgrade dashboard, transactions, and chat pages to use authenticated APIs.
- [ ] Run `cd frontend && npm run build`.

### Task 6: Workflow and verification

- [ ] Rewrite `docs/WORKFLOW.md` as canonical project workflow.
- [ ] Run backend tests.
- [ ] Run frontend build.
- [ ] If local services can run, browser-smoke the flow.

