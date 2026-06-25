"""expense → transaction rename + type column

Revision ID: 2a3b4c5d6e7f
Revises: 18bd2b52ba1e
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '2a3b4c5d6e7f'
down_revision: str | Sequence[str] | None = '18bd2b52ba1e'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Rename tables
    op.rename_table("expense", "transaction")
    op.rename_table("expense_category", "category")
    op.rename_table("expense_tag", "tag")
    op.rename_table("expense_tag_index", "transaction_tag")

    # 2. Add type column to transaction (existing data = all expense)
    op.add_column("transaction", sa.Column("type", sa.String(7), nullable=False, server_default="expense"))

    # 3. Rename expense_id → transaction_id in transaction_tag
    op.alter_column("transaction_tag", "expense_id", new_column_name="transaction_id")

    # 4. Rename indexes for transaction table
    op.execute("ALTER INDEX idx_expense_uid_deleted_time RENAME TO idx_transaction_uid_deleted_time")
    op.execute("ALTER INDEX idx_expense_uid_deleted_category RENAME TO idx_transaction_uid_deleted_category")

    # 5. Update transaction_tag indexes
    op.execute("DROP INDEX IF EXISTS idx_tag_index_expense")
    op.execute("CREATE INDEX idx_tag_index_transaction ON transaction_tag(transaction_id)")

    # 6. Update index definitions for category/tag (remove deleted column references)
    op.execute("DROP INDEX IF EXISTS idx_category_uid_deleted")
    op.execute("DROP INDEX IF EXISTS idx_tag_uid_deleted")
    op.execute("CREATE INDEX idx_category_uid_order ON category(uid, display_order)")
    op.execute("CREATE INDEX idx_tag_uid_order ON tag(uid, display_order)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_category_uid_order")
    op.execute("DROP INDEX IF EXISTS idx_tag_uid_order")
    op.execute("DROP INDEX IF EXISTS idx_tag_index_transaction")
    op.execute("CREATE INDEX idx_tag_index_expense ON expense_tag_index(expense_id)")
    op.drop_column("transaction", "type")
    op.alter_column("transaction_tag", "transaction_id", new_column_name="expense_id")
    op.execute("ALTER TABLE transaction_tag RENAME TO expense_tag_index")
    op.execute("ALTER TABLE tag RENAME TO expense_tag")
    op.execute("ALTER TABLE category RENAME TO expense_category")
    op.execute("ALTER TABLE transaction RENAME TO expense")
