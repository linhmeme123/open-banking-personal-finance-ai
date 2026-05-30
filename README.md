# Open Banking Personal Finance AI

**Starter project cho portfolio fintech/banking**: Ứng dụng quản lý tài chính cá nhân hoàn chỉnh dùng dữ liệu Open Banking giả lập, AI phân loại giao dịch tự động, AI financial coach, dashboard chi tiêu thông minh, và consent ledger audit mô phỏng blockchain.

---

## 📋 Mục tiêu dự án

Dự án này giúp bạn thể hiện **4 yêu cầu chính** mà các công ty fintech/banking tìm kiếm:

### 1. 🏦 **Digital Banking / Open Banking**
- Kết nối tài khoản từ nhiều ngân hàng giả lập (Bank A, Bank B, E-Wallet)
- Chuẩn hóa dữ liệu account, balance, transaction từ các nguồn khác nhau
- Thiết kế REST API giống sản phẩm tài chính thật
- Xử lý sandbox provider mock giống Open Banking thực tế

### 2. 🤖 **AI Personal Finance**
- **AI Categorizer**: Tự động phân loại giao dịch (ăn uống, giao thông, mua sắm, v.v.) với confidence score
- **AI Coach**: Chatbot hỏi đáp tài chính dựa trên dữ liệu transaction cá nhân
- Phân tích hành vi chi tiêu: Spending by category, monthly cashflow, recurring subscriptions
- Phát hiện chi tiêu bất thường

### 3. 💼 **Backend Fintech Architecture**
- REST API thiết kế chuyên nghiệp với FastAPI
- PostgreSQL data model rõ ràng dùng SQLAlchemy ORM
- Service layer tách biệt (không business logic trong API)
- Authentication lite (demo token)
- Error handling và validation chuẩn

### 4. 🔐 **Blockchain-inspired Audit & Compliance**
- Bảng `consent_events` ghi lại mỗi lần user cấp/thu hồi quyền
- Event hash để mô phỏng blockchain audit trail
- Privacy-first design: Chứng minh user consent trước khi truy cập dữ liệu
- Có thể nâng cấp lưu hash consent lên smart contract

---

## 🏗️ Kiến trúc tổng quan

```txt
┌─────────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                          │
│  - Home / Demo Sign-in                                         │
│  - Connect Bank (Sandbox Provider Selection)                   │
│  - Accounts Dashboard                                          │
│  - Transactions List (AI-categorized)                          │
│  - Budgets & Spending Insights                                 │
│  - Consent Audit Trail                                         │
│  - AI Coach Chatbot                                            │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     │ REST API + Bearer Token
                     │ (http://localhost:8000)
                     │
┌────────────────────▼────────────────────────────────────────────┐
│                Backend (FastAPI)                                │
├─────────────────────────────────────────────────────────────────┤
│  Service Layer:                                                 │
│  ├─ Auth Service (demo token validation)                        │
│  ├─ Open Banking Mock Provider                                  │
│  ├─ Transaction Sync & Normalization                            │
│  ├─ AI Categorizer (rule-based → ML)                            │
│  ├─ AI Financial Coach (mock → LLM)                             │
│  ├─ Consent & Audit Manager                                     │
│  └─ Insights Calculator                                         │
│                                                                 │
│  API Routes:                                                    │
│  └─ /api/{accounts, transactions, insights, ai, consents}      │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     │ SQLAlchemy ORM
                     │
┌────────────────────▼────────────────────────────────────────────┐
│              PostgreSQL Database                                │
├─────────────────────────────────────────────────────────────────┤
│  Core Tables:                                                   │
│  ├─ users (demo identity)                                       │
│  ├─ bank_providers (sandbox registry)                           │
│  ├─ bank_connections (user-provider link + last sync)           │
│  ├─ accounts (normalized bank accounts)                         │
│  ├─ transactions (with AI category + confidence)                │
│  ├─ categories (category dictionary)                            │
│  ├─ budgets (monthly category limits)                           │
│  ├─ consent_events (audit trail with hash)                      │
│  ├─ recurring_payments (subscription detection)                 │
│  └─ ai_chat_messages (conversation history)                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## ✨ Tính năng hiện tại trong starter

- ✅ Dashboard mock UI (Next.js)
- ✅ Trang transactions với filtering
- ✅ Trang AI chat
- ✅ FastAPI backend với service layer
- ✅ Mock Open Banking transaction data
- ✅ Rule-based AI categorizer mở đầu
- ✅ AI coach service mock (dễ thay bằng LLM thật)
- ✅ PostgreSQL schema hoàn chỉnh với SQLAlchemy
- ✅ Docker Compose (database + backend + frontend)
- ✅ Seed script tạo dữ liệu demo

---

## 🛣️ Roadmap 6 tuần

### **Tuần 1: Foundation** 🟢 BASE
**Mục tiêu**: Xây dựng base chạy được
- [ ] Chạy được frontend, backend, database (Docker Compose)
- [ ] Hiểu data model: users, accounts, transactions, categories, consent_events
- [ ] Hiển thị transaction từ API lên frontend
- [ ] Demo login + cấp consent lần đầu
- **Deliverable**: Full stack chạy, user thấy dữ liệu

### **Tuần 2: Open Banking Sandbox** 🟡 MOCK DATA
**Mục tiêu**: Account aggregation từ nhiều nguồn
- [ ] Thêm mock provider: Bank A, Bank B, E-wallet
- [ ] Tạo endpoint `POST /api/open-banking/sync` (kéo dữ liệu từ provider)
- [ ] Chuẩn hóa transaction format (normalize currency, timestamp, description)
- [ ] Tính toán account balance tổng hợp
- **Deliverable**: User sync được transactions từ 3 ngân hàng, thấy tổng balance

### **Tuần 3: AI Transaction Categorization** 🤖 AI PHASE 1
**Mục tiêu**: Auto-categorize transactions
- [ ] Bản đầu: Rule-based categorizer (regex + keyword matching)
- [ ] Bản sau: ML model (scikit-learn text classifier hoặc embedding)
- [ ] Lưu `category` + `category_confidence` trong transaction
- [ ] API endpoint `POST /api/ai/categorize`
- **Deliverable**: Mỗi transaction tự động có danh mục + độ tin cậy

### **Tuần 4: Personal Finance Insights** 📊 ANALYTICS
**Mục tiêu**: Dashboard thông minh
- [ ] Spending by category (pie chart, bar chart)
- [ ] Monthly cashflow (income vs expense)
- [ ] Recurring subscriptions detection
- [ ] Abnormal spending detection (spike alert)
- [ ] Endpoint `GET /api/insights/monthly-summary`
- **Deliverable**: Dashboard hiển thị insights thực tế từ dữ liệu

### **Tuần 5: AI Financial Coach** 🤖 AI PHASE 2
**Mục tiêu**: Chatbot thông minh
- [ ] Chatbot hỏi đáp: "Tháng này tôi chi bao nhiêu cho ăn uống?"
- [ ] RAG nhỏ trên dữ liệu transaction của user
- [ ] Function calling: `get_transactions()`, `get_spending_by_category()`, `get_budget_status()`
- [ ] Gợi ý tiết kiệm cá nhân hóa
- [ ] Endpoint `POST /api/ai/chat`
- [ ] Lưu chat history trong database
- **Deliverable**: User hỏi AI và nhận câu trả lời based on real data

### **Tuần 6: Portfolio Polish** 🚀 PRODUCTION
**Mục tiêu**: Deploy & documentation
- [ ] Deploy (Heroku / Vercel / AWS)
- [ ] Viết README kỹ (như file này!)
- [ ] Thêm architecture diagram (Mermaid)
- [ ] Thêm demo video (loom.com)
- [ ] Thêm test cases (pytest backend, Jest frontend)
- [ ] Setup CI/CD
- **Deliverable**: Production-ready project trên GitHub

---

## 🚀 Cách chạy bằng Docker (Recommended)

```bash
# Build và chạy tất cả services
docker compose up --build

# URL sau khi chạy:
# Frontend:         http://localhost:3000
# Backend Swagger:  http://localhost:8000/docs
# PostgreSQL:       localhost:5432 (user: postgres, password: postgres)
```

---

## 🔧 Cách chạy thủ công (Development)

### Backend (Terminal 1)

```bash
cd backend

# Tạo virtual environment
python -m venv .venv
source .venv/bin/activate  # Mac/Linux
# .venv\Scripts\activate  # Windows

# Cài dependencies
pip install -r requirements.txt

# ===== DATABASE MIGRATION (Alembic) =====

# Tạo database trước (nếu chưa có)
# createdb open_banking

# Chạy migration lần đầu (áp dụng tất cả migrations)
alembic upgrade head

# Chạy backend
uvicorn app.main:app --reload --port 8000
```

Backend sẽ chạy ở: **http://localhost:8000**  
Swagger docs: **http://localhost:8000/docs**

---

### 🗂️ Alembic - Database Schema Management

**Alembic** giúp quản lý thay đổi database schema một cách an toàn (version control cho database).

#### **Setup Alembic lần đầu** (đã có sẵn)

```bash
cd backend

# Nếu chưa cài Alembic
pip install alembic

# Khởi tạo Alembic folder (chỉ cần 1 lần)
# alembic init alembic
```

#### **Workflow: Thay đổi Database Schema**

**Bước 1: Sửa model trong code**

```python
# filepath: backend/app/models/domain.py
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True)
    description = Column(String(500))
    # Thêm cột mới
    merchant_category = Column(String(100), nullable=True)  # ← THÊM DÒNG NÀY
```

**Bước 2: Tạo migration file (tự động tạo từ model)**

```bash
cd backend

# Tạo migration file mới (Alembic tự detect thay đổi)
alembic revision --autogenerate -m "Add merchant_category to transactions"

# ✅ Kết quả: File mới được tạo trong `alembic/versions/`
# Ví dụ: 2026_05_24_add_merchant_category.py
```

**Bước 3: Kiểm tra migration file (QUAN TRỌNG!)**

```bash
# Mở file vừa tạo để xem
cat alembic/versions/2026_05_24_add_merchant_category.py
```

Nội dung sẽ giống như:
```python
# filepath: backend/alembic/versions/2026_05_24_add_merchant_category.py
from alembic import op
import sqlalchemy as sa

def upgrade() -> None:
    # Chạy khi apply migration
    op.add_column('transactions', sa.Column('merchant_category', sa.String(100), nullable=True))

def downgrade() -> None:
    # Chạy khi rollback migration
    op.drop_column('transactions', 'merchant_category')
```

**⚠️ Luôn kiểm tra migration file trước khi apply!** Đôi khi Alembic tạo không hoàn toàn đúng.

**Bước 4: Apply migration lên database**

```bash
# Apply migration mới nhất
alembic upgrade head

# ✅ Kết quả: Cột `merchant_category` được thêm vào table `transactions`
```

**Bước 5: Kiểm tra database**

```bash
# Kết nối database để xem schema
psql -U postgres -d open_banking

# Query để xem columns trong table
\d transactions

# Hoặc dùng SQL
SELECT column_name, data_type FROM information_schema.columns 
WHERE table_name = 'transactions';
```

#### **Các lệnh Alembic thường dùng**

| Lệnh | Mục đích |
|------|---------|
| `alembic upgrade head` | Apply tất cả migrations chưa áp dụng |
| `alembic downgrade -1` | Rollback migration gần nhất |
| `alembic current` | Xem current migration version |
| `alembic history` | Xem tất cả migrations |
| `alembic revision --autogenerate -m "message"` | Tạo migration mới từ model changes |
| `alembic merge` | Merge 2 migration branches (nếu conflict) |

#### **Ví dụ thực tế: Thêm cột `last_sync_at` vào BankConnection**

**Bước 1: Sửa model**
```python
# filepath: backend/app/models/domain.py
from datetime import datetime

class BankConnection(Base):
    __tablename__ = "bank_connections"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    provider_code = Column(String(50))
    # Thêm cột này
    last_sync_at = Column(DateTime, default=datetime.utcnow, nullable=True)
```

**Bước 2: Tạo migration**
```bash
alembic revision --autogenerate -m "Add last_sync_at to bank_connections"
```

**Bước 3: Kiểm tra file**
```bash
cat alembic/versions/2026_05_24_add_last_sync_at.py
# Xem xem migrate file có đúng không
```

**Bước 4: Apply migration**
```bash
alembic upgrade head
```

**Bước 5: Xác nhận**
```bash
alembic current
# Output: e12345abcd (hash của migration vừa apply)
```

#### **Best Practices**

✅ **Nên làm:**
- Tạo 1 migration cho 1 thay đổi logic
- Luôn kiểm tra migration file trước apply
- Commit migration file lên Git cùng code
- Viết message rõ ràng: `"Add user_id index to transactions"`

❌ **Không nên làm:**
- Chỉnh sửa migration file đã apply
- Apply multiple migrations cùng lúc mà không kiểm tra
- Xóa migration file cũ (sẽ vỡ version history)
- Manual sửa database mà không qua Alembic

#### **Database Reset (Clean Slate)**

Nếu muốn xóa tất cả migrations và bắt đầu lại:

```bash
# ⚠️ CẬP NHẬT: Chỉ nên làm trong development!

# Downgrade tất cả migrations
alembic downgrade base

# Hoặc xóa database và tạo lại
dropdb open_banking
createdb open_banking

# Áp dụng lại tất cả migrations
alembic upgrade head
```

---

### Frontend (Terminal 2)

```bash
cd frontend

# Cài dependencies
npm install

# Chạy dev server
npm run dev
```

Frontend sẽ chạy ở: **http://localhost:3000**

### Database (Terminal 3 - Optional)

Nếu không dùng Docker:

```bash
# Cần cài PostgreSQL trước
# Mac: brew install postgresql
# Linux: sudo apt-get install postgresql
# Windows: Download từ postgresql.org

# Khởi động PostgreSQL
postgres -D /usr/local/var/postgres

# Hoặc tạo database nếu chưa có
createdb open_banking

# Hoặc dùng Docker chỉ cho DB
docker run --name postgres_open_banking \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=open_banking \
  -p 5432:5432 \
  -d postgres:15
```

---

## 📡 Endpoint chính

### Health Check
```
GET /health
Response: {"status": "ok"}
```

### Accounts
```
GET /api/accounts
Response: [
  {
    "id": 1,
    "account_name": "Tài khoản tiền lương",
    "account_type": "checking",
    "balance": 50000000,
    "currency": "VND",
    "provider_name": "BANK_A"
  }
]
```

### Transactions
```
GET /api/transactions?limit=20&offset=0
Response: [
  {
    "id": 1,
    "transaction_time": "2026-05-24T09:30:00",
    "description": "Thanh toán Starbucks",
    "merchant_name": "Starbucks Coffee",
    "amount": 150000,
    "currency": "VND",
    "direction": "expense",
    "category": "Food & Drink",
    "category_confidence": 0.95
  }
]
```

### Insights
```
GET /api/insights/monthly-summary?year=2026&month=5
Response: {
  "total_income": 100000000,
  "total_expense": 25000000,
  "spending_by_category": {
    "Food & Drink": 3500000,
    "Transportation": 2000000,
    "Shopping": 8000000,
    "Others": 11500000
  },
  "recurring_subscriptions": [
    {
      "name": "Netflix",
      "amount": 150000,
      "frequency": "monthly"
    }
  ]
}
```

### Open Banking Sync
```
POST /api/open-banking/sync
Body: {
  "user_id": 1,
  "provider_code": "BANK_A"
}
Response: {
  "status": "success",
  "accounts_synced": 2,
  "transactions_synced": 45,
  "last_sync": "2026-05-24T09:30:00"
}
```

### AI Categorize
```
POST /api/ai/categorize
Body: {
  "transaction_id": 123
}
Response: {
  "transaction_id": 123,
  "category": "Food & Drink",
  "confidence": 0.95
}
```

### AI Chat
```
POST /api/ai/chat
Body: {
  "user_id": 1,
  "message": "Tháng này tôi chi bao nhiêu cho ăn uống?"
}
Response: {
  "answer": "Bạn chi 3,500,000 VND cho ăn uống tháng 5, tăng 15% so với tháng trước. Gợi ý: cắt giảm 2-3 lần ăn ngoài/tuần để tiết kiệm ~500k/tháng."
}
```

### Consents
```
POST /api/consents
Body: {
  "user_id": 1,
  "provider_code": "BANK_A",
  "scope": "accounts:read transactions:read",
  "action": "granted"
}
Response: {
  "id": 1,
  "provider_code": "BANK_A",
  "scope": "accounts:read transactions:read",
  "action": "granted",
  "event_hash": "abc123def456...",
  "created_at": "2026-05-24T09:30:00"
}
```

---

## 🎯 Cách nâng cấp AI thật

### AI Categorizer - Nâng cấp thành ML

**Option 1: Scikit-learn (Recommended cho demo)**
```bash
pip install scikit-learn pandas
```

**Option 2: OpenAI Classification**
```bash
pip install openai
```

### AI Coach - Nâng cấp thành LLM thực

Thay file `backend/app/ai/coach.py` bằng một trong các option:

#### **Option A: OpenAI API** (Powerful, có phí)
```bash
pip install openai langchain
export OPENAI_API_KEY="sk-..."
```

#### **Option B: Local LLM với Ollama** (Miễn phí, chạy local)
```bash
# Cài Ollama: https://ollama.ai
ollama pull mistral
# Chạy local server: ollama serve
```

#### **Option C: LangChain + Tools** (Best practice)
```bash
pip install langchain langchain-openai
```

LangChain sẽ cho phép AI Coach gọi tools:
- `get_transactions(user_id, category, date_range)`
- `get_spending_by_category(user_id)`
- `get_budget_status(user_id, category)`
- `get_recurring_subscriptions(user_id)`

---

## ⛓️ Cách nâng cấp Blockchain Audit

### Phase 1: Current (Database-based)
- ✅ Bảng `consent_events` ghi lại mỗi action
- ✅ `event_hash` = SHA-256(user_id + provider + action + timestamp)
- ✅ Lưu trong database

### Phase 2: Smart Contract Integration
- [ ] Kết nối Web3 library (web3.py, ethers.js)
- [ ] Ghi `event_hash` lên Ethereum / Polygon smart contract
- [ ] Lưu `tx_hash` từ blockchain vào database
- [ ] Tạo trang "Consent Audit Trail" hiển thị link blockchain explorer

### Phase 3: Full Blockchain Audit
```solidity
// Contract.sol
mapping(bytes32 => bool) public consentEvents;

function recordConsent(bytes32 eventHash) public {
    consentEvents[eventHash] = true;
    emit ConsentRecorded(eventHash, block.timestamp);
}
```

---

## 📚 Vì sao project này phù hợp CV ngân hàng

Project này chứng minh bạn hiểu & có thể thực hiện:

1. ✅ **Open Banking Architecture**
   - Account aggregation từ nhiều nguồn
   - Sandbox provider simulation

2. ✅ **Digital Banking Product Flow**
   - User consent & permission scopes
   - Transaction sync & normalization
   - Dashboard & insights

3. ✅ **Data Privacy & Compliance**
   - User consent management (GDPR-like)
   - Audit trail & blockchain-ready hash
   - Permission-based data access

4. ✅ **Personal Finance Analytics**
   - Transaction categorization
   - Spending analysis
   - Recurring payment detection
   - Abnormal spending alerts

5. ✅ **AI/ML on Financial Data**
   - Rule-based + ML categorization
   - RAG chatbot using transaction data
   - LLM integration (OpenAI, Ollama)

6. ✅ **Backend Fintech Architecture**
   - REST API design
   - Service layer pattern
   - PostgreSQL data modeling
   - Error handling & validation

---

## 📦 Tech Stack

| Layer | Tech | Version |
|-------|------|---------|
| **Frontend** | Next.js, React, TypeScript | 14+ |
| **Backend** | FastAPI, Python, Pydantic | 3.11+ |
| **Database** | PostgreSQL, SQLAlchemy | 15+, 2.0+ |
| **AI** | LangChain, OpenAI / Ollama | Latest |
| **DevOps** | Docker, Docker Compose | 24+ |
| **Testing** | pytest, Jest | Latest |

---

## 🧪 Testing (Tuần 6)

### Backend Tests
```bash
cd backend
pip install pytest pytest-cov
pytest --cov=app tests/
```

### Frontend Tests
```bash
cd frontend
npm install --save-dev jest @testing-library/react
npm test
```

---

## 🚀 Deployment

### Option 1: Heroku (Dễ nhất)
```bash
# Backend
git push heroku main

# Frontend (Vercel)
npm install -g vercel
vercel
```

### Option 2: AWS / Google Cloud / Azure
- Backend: Cloud Run / App Engine
- Frontend: S3 + CloudFront / Cloud Storage + CDN
- Database: Managed PostgreSQL (RDS / Cloud SQL)

---

## 🤝 Cộng tác & Feedback

Nếu bạn là **nhà tuyển dụng** / **HR**, project này chứng minh ứng viên hiểu:
- ✅ Fintech product architecture
- ✅ Digital banking flow
- ✅ Full-stack development
- ✅ AI/ML integration
- ✅ Compliance & security
- ✅ Professional coding standards

---

## 📝 License

MIT License - Feel free to use for portfolio & learning

---

## 📞 Support

**Swagger API Docs**: http://localhost:8000/docs  
**GitHub Issues**: [Repository Issues]  
**Portfolio**: [Your LinkedIn / Website]

---

**Made with ❤️ for fintech enthusiasts**