"""Fix alembic version

Revision ID: 4d5e6f7a8b9c
Revises: 3c4d5e6f7a8b
"""
from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '4d5e6f7a8b9c'
down_revision: str | Sequence[str] | None = '3c4d5e6f7a8b'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
