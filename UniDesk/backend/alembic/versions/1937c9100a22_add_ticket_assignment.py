"""add ticket assignment

Revision ID: 1937c9100a22
Revises: e589999d3e31
Create Date: 2026-08-28 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1937c9100a22'
down_revision: Union[str, Sequence[str], None] = 'e589999d3e31'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('tickets', sa.Column('assigned_to', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_tickets_assigned_to'), 'tickets', ['assigned_to'], unique=False)
    op.create_foreign_key(
        'fk_tickets_assigned_to_users',
        'tickets',
        'users',
        ['assigned_to'],
        ['id'],
        ondelete='SET NULL',
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('fk_tickets_assigned_to_users', 'tickets', type_='foreignkey')
    op.drop_index(op.f('ix_tickets_assigned_to'), table_name='tickets')
    op.drop_column('tickets', 'assigned_to')
