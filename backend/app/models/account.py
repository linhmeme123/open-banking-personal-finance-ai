from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "provider_id",
            "external_account_id",
            name="uq_user_provider_external_account",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    provider_id: Mapped[int] = mapped_column(ForeignKey("bank_providers.id"))
    external_account_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    account_name: Mapped[str] = mapped_column(String(255))
    account_type: Mapped[str] = mapped_column(String(50))
    currency: Mapped[str] = mapped_column(String(10), default="VND")
    balance: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)

    user = relationship("User", back_populates="accounts")
    provider = relationship("BankProvider", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account")
