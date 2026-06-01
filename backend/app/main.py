from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

import app.models
from app.api import (
    accounts,
    ai,
    auth,
    budgets,
    consents,
    insights,
    mock_bank,
    open_banking,
    transactions,
    webhooks,
    users,
)
from app.core.config import settings
from app.db.session import Base, engine


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="A fintech portfolio project for open banking, personal finance analytics, and AI coaching.",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app.mount(
    "/uploads",
    StaticFiles(directory=UPLOAD_DIR),
    name="uploads",
)


app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(accounts.router, prefix="/api/accounts", tags=["accounts"])
app.include_router(transactions.router, prefix="/api/transactions", tags=["transactions"])
app.include_router(insights.router, prefix="/api/insights", tags=["insights"])
app.include_router(open_banking.router, prefix="/api/open-banking", tags=["open-banking"])
app.include_router(mock_bank.router, prefix="/api/mock-bank", tags=["mock-bank"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["webhooks"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])
app.include_router(consents.router, prefix="/api/consents", tags=["consents"])
app.include_router(budgets.router, prefix="/api/budgets", tags=["budgets"])


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "open-banking-personal-finance-ai",
    }
