from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class BankProvider(Base):
    __tablename__ = "bank_providers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    provider_type: Mapped[str] = mapped_column("type", String(50), default="traditional_bank")
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="available")
    supported_scopes: Mapped[list[str]] = mapped_column(JSON, default=list)

    accounts = relationship("Account", back_populates="provider")
    bank_connections = relationship("BankConnection", back_populates="provider")


class BankConnection(Base):
    __tablename__ = "bank_connections"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "provider_id",
            name="uq_user_provider_connection",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    provider_id: Mapped[int] = mapped_column(ForeignKey("bank_providers.id"))
    status: Mapped[str] = mapped_column(String(50), default="connected")
    consent_scope: Mapped[str] = mapped_column(String(255))
    connected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    user = relationship("User", back_populates="bank_connections")
    provider = relationship("BankProvider", back_populates="bank_connections")
