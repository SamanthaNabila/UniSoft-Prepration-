"""add ticket assignment

Revision ID: a1b2c3d4e5f6
Revises: e589999d3e31
Create Date: 2026-08-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "e589999d3e31"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("tickets", sa.Column("assigned_to", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_tickets_assigned_to_users",
        "tickets",
        "users",
        ["assigned_to"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_tickets_assigned_to_users", "tickets", type_="foreignkey")
    op.drop_column("tickets", "assigned_to")