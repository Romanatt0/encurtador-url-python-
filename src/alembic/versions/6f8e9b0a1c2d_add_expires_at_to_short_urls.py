"""add expires_at to short_urls

Revision ID: 6f8e9b0a1c2d
Revises: ffaeb92272a5
Create Date: 2026-06-19 21:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6f8e9b0a1c2d'
down_revision: Union[str, Sequence[str], None] = 'ffaeb92272a5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('short_urls', sa.Column('expires_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column('short_urls', 'expires_at')
