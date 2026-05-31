"""add external account id

Revision ID: 5f4a730e87c1
Revises: 9c841cb0a31d
Create Date: 2026-06-01 01:30:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "5f4a730e87c1"
down_revision: Union[str, Sequence[str], None] = "9c841cb0a31d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("accounts", sa.Column("external_account_id", sa.String(length=255), nullable=True))
    op.create_unique_constraint(
        "uq_user_provider_external_account",
        "accounts",
        ["user_id", "provider_id", "external_account_id"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_user_provider_external_account", "accounts", type_="unique")
    op.drop_column("accounts", "external_account_id")
