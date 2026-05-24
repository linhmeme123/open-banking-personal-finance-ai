from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

#thông tin tài khoản trả về khi user gọi GET /api/accounts
class AccountOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    account_name: str
    account_type: str
    currency: str
    balance: Decimal
    provider_name: str

#thông tin giao dịch trả về khi user gọi GET /api/transactions
class TransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    transaction_time: datetime
    description: str
    merchant_name: str | None
    amount: Decimal
    currency: str
    direction: str #income(nhận) | expense(chi)
    category: str | None
    category_confidence: Decimal | None

#User gửi POST /api/ai/chat
class ChatRequest(BaseModel):
    message: str

#Trả về câu trả lời từ AI Financial Coach
class ChatResponse(BaseModel):
    answer: str

#User gửi POST /api/transactions/categorize để yêu cầu phân loại giao dịch
class CategorizeRequest(BaseModel):
    transaction_id: int

#Trả về kết quả phân loại cho giao dịch
class CategorizeResponse(BaseModel):
    transaction_id: int
    category: str
    confidence: float

#User gửi POST /api/consents để tạo sự kiện cấp quyền mới
class ConsentCreate(BaseModel):
    provider_code: str
    scope: str#phạm vi quyền hạn (ví dụ: "accounts:read transactions:read")
    action: str

#Trả về thông tin sự kiện cấp quyền khi user xem lịch sử consent 
class ConsentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    provider_code: str
    scope: str
    action: str
    event_hash: str
    created_at: datetime



class ProviderConnectRequest(BaseModel):
    provider_code: str
    scope: str = "accounts:read transactions:read"


class SyncRequest(BaseModel):
    provider_code: str = "BANK_A"


class BankConnectionOut(BaseModel):
    id: int
    provider_code: str
    provider_name: str
    status: str
    consent_scope: str
    last_synced_at: datetime | None


class BudgetCreate(BaseModel):
    category: str
    month: str
    monthly_limit: Decimal


class BudgetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category: str
    month: str
    monthly_limit: Decimal


class AiChatMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
    content: str
    created_at: datetime
