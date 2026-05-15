# Open Banking Personal Finance AI

Starter project cho portfolio fintech/banking: một ứng dụng quản lý tài chính cá nhân dùng dữ liệu Open Banking giả lập, AI phân loại giao dịch, AI financial coach, dashboard chi tiêu, và consent ledger mô phỏng.

## 1. Mục tiêu dự án

Dự án này giúp bạn thể hiện năng lực ở 4 mảng ngân hàng/fintech:

1. **Digital Banking / Open Banking**
   - Kết nối tài khoản ngân hàng giả lập.
   - Chuẩn hóa account, balance, transaction.
   - Thiết kế API giống sản phẩm tài chính thật.

2. **AI Personal Finance**
   - Phân loại giao dịch tự động.
   - Phân tích hành vi chi tiêu.
   - Chatbot hỏi đáp dữ liệu tài chính cá nhân.

3. **Backend Fintech**
   - REST API.
   - PostgreSQL data model.
   - Service layer rõ ràng.
   - Audit log và consent model.

4. **Blockchain-inspired Audit**
   - Có bảng `consent_events` để mô phỏng user consent ledger.
   - Giai đoạn sau có thể lưu hash consent lên smart contract.

## 2. Kiến trúc tổng quan

```txt
Frontend Next.js
  |
  | REST API
  v
Backend FastAPI
  |
  | SQLAlchemy
  v
PostgreSQL
  |
  +-- AI Categorizer
  +-- AI Financial Coach
  +-- Open Banking Mock Provider
  +-- Consent/Audit Service
```

## 3. Tính năng hiện tại trong starter

- Dashboard mock UI.
- Trang transactions.
- Trang AI chat.
- FastAPI backend.
- Mock Open Banking transaction data.
- Rule-based AI categorizer mở đầu.
- AI coach service mock, dễ thay bằng LLM thật.
- PostgreSQL schema bằng SQLAlchemy.
- Docker Compose cho database + backend + frontend.
- Seed script tạo dữ liệu demo.

## 4. Roadmap 6 tuần

### Tuần 1: Foundation
- Chạy được frontend, backend, database.
- Hiểu data model: users, accounts, transactions, categories, consent_events.
- Hiển thị transaction từ API lên frontend.

### Tuần 2: Open Banking Sandbox
- Thêm mock provider: Bank A, Bank B, E-wallet.
- Tạo endpoint sync transactions.
- Chuẩn hóa transaction format.

### Tuần 3: AI Transaction Categorization
- Bản đầu: rule-based categorizer.
- Bản sau: train model scikit-learn hoặc dùng embedding + classifier.
- Lưu confidence score.

### Tuần 4: Personal Finance Insights
- Spending by category.
- Monthly cashflow.
- Recurring subscriptions.
- Abnormal spending detection.

### Tuần 5: AI Financial Coach
- Chatbot hỏi đáp: “Tháng này tôi chi bao nhiêu cho ăn uống?”
- RAG nhỏ trên dữ liệu transaction của user.
- Gợi ý tiết kiệm cá nhân hóa.

### Tuần 6: Portfolio Polish
- Deploy.
- Viết README kỹ.
- Thêm architecture diagram.
- Thêm demo video.
- Thêm test cases.

## 5. Cách chạy bằng Docker

```bash
docker compose up --build
```

Frontend: http://localhost:3000  
Backend docs: http://localhost:8000/docs  
PostgreSQL: localhost:5432

## 6. Cách chạy thủ công

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## 7. Endpoint chính

```txt
GET  /health
GET  /api/accounts
GET  /api/transactions
GET  /api/insights/monthly-summary
POST /api/open-banking/sync
POST /api/ai/categorize
POST /api/ai/chat
POST /api/consents
```

## 8. Hướng nâng cấp AI thật

Bạn có thể thay `backend/app/ai/coach.py` bằng:
- OpenAI API.
- Local LLM qua Ollama.
- LlamaIndex/LangChain.
- RAG trên bảng transactions.
- Function calling để gọi tools: get_transactions, get_spending_by_category, get_budget_status.

## 9. Hướng nâng cấp blockchain

Ở giai đoạn đầu, chỉ cần bảng `consent_events`.
Sau đó nâng cấp:
- Hash consent event.
- Ghi hash lên smart contract.
- Lưu tx_hash vào database.
- Tạo trang “Consent Audit Trail”.

## 10. Vì sao project này hợp CV ngân hàng

Project này chứng minh bạn hiểu:
- Open Banking.
- Digital banking product flow.
- Data privacy và user consent.
- Personal finance analytics.
- AI ứng dụng trên dữ liệu tài chính.
- Backend API cho hệ thống fintech.
