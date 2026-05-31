"""extend bank provider metadata

Revision ID: 9c841cb0a31d
Revises: 05381cfed46e
Create Date: 2026-06-01 00:30:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9c841cb0a31d"
down_revision: Union[str, Sequence[str], None] = "05381cfed46e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "bank_providers",
        sa.Column("type", sa.String(length=50), nullable=False, server_default="traditional_bank"),
    )
    op.add_column("bank_providers", sa.Column("logo_url", sa.String(length=500), nullable=True))
    op.add_column(
        "bank_providers",
        sa.Column("status", sa.String(length=50), nullable=False, server_default="available"),
    )
    op.add_column(
        "bank_providers",
        sa.Column(
            "supported_scopes",
            sa.JSON(),
            nullable=False,
            server_default='["accounts:read", "transactions:read", "balance:read"]',
        ),
    )

    # Preserve data created by the original sandbox while moving it onto the
    # provider codes used by the extended mock abstraction.
    op.execute(
        "UPDATE bank_providers SET code = 'TIMO', name = 'Timo', type = 'digital_bank' "
        "WHERE code = 'BANK_A'"
    )
    op.execute(
        "UPDATE bank_providers SET code = 'TECHCOMBANK', name = 'Techcombank', type = 'traditional_bank' "
        "WHERE code = 'BANK_B'"
    )
    op.execute(
        "UPDATE bank_providers SET code = 'MOMO', name = 'MoMo', type = 'fintech' "
        "WHERE code = 'EWALLET_X'"
    )


def downgrade() -> None:
    op.drop_column("bank_providers", "supported_scopes")
    op.drop_column("bank_providers", "status")
    op.drop_column("bank_providers", "logo_url")
    op.drop_column("bank_providers", "type")
