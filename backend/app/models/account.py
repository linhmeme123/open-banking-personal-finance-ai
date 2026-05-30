from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    provider_id: Mapped[int] = mapped_column(ForeignKey("bank_providers.id"))
    account_name: Mapped[str] = mapped_column(String(255))
    account_type: Mapped[str] = mapped_column(String(50))
    currency: Mapped[str] = mapped_column(String(10), default="VND")
    balance: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)

    user = relationship("User", back_populates="accounts")
    provider = relationship("BankProvider", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account")