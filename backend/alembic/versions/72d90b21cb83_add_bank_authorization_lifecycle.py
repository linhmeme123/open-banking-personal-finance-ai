"""add bank authorization lifecycle

Revision ID: 72d90b21cb83
Revises: cfccfe957f37
Create Date: 2026-06-02 00:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "72d90b21cb83"
down_revision: Union[str, Sequence[str], None] = "cfccfe957f37"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "bank_connections",
        sa.Column("selected_account_ids", sa.JSON(), nullable=False, server_default="[]"),
    )
    with op.batch_alter_table("bank_connections") as batch_op:
        batch_op.alter_column("connected_at", existing_type=sa.DateTime(), nullable=True)


def downgrade() -> None:
    with op.batch_alter_table("bank_connections") as batch_op:
        batch_op.alter_column("connected_at", existing_type=sa.DateTime(), nullable=False)
    op.drop_column("bank_connections", "selected_account_ids")
