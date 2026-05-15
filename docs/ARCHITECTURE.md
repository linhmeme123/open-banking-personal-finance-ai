# Architecture

```txt
[Next.js Client]
  - Dashboard
  - Transactions
  - AI Chat
  - Consent Management
        |
        v
[FastAPI Backend]
  - REST Controllers
  - Service Layer
  - AI Layer
  - Open Banking Mock Adapter
        |
        v
[PostgreSQL]
  - users
  - bank_providers
  - accounts
  - transactions
  - categories
  - consent_events
  - ai_chat_messages
```

## Design Principles

1. **Separation of concerns**
   - API routes chỉ nhận request và trả response.
   - Services xử lý business logic.
   - Models chỉ định nghĩa database schema.
   - AI module xử lý classification/chat logic.

2. **Banking-style auditability**
   - Consent event lưu đầy đủ action, scope, timestamp.
   - Transaction categorization lưu confidence.

3. **Extensible AI**
   - Bản đầu dùng rule-based và mock LLM.
   - Sau đó thay bằng model thật mà không phải sửa toàn bộ app.

4. **Open Banking abstraction**
   - Backend không phụ thuộc trực tiếp vào một ngân hàng.
   - Có provider interface để thêm Bank A, Bank B, E-wallet.
