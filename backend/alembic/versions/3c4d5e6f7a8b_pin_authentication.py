"""PIN authentication migration

Revision ID: 3c4d5e6f7a8b
Revises: 2a3b4c5d6e7f
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '3c4d5e6f7a8b'
down_revision: str | Sequence[str] | None = '2a3b4c5d6e7f'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Drop email column
    op.drop_column("user", "email")

    # 2. Add PIN-related columns
    op.add_column("user", sa.Column("pin_changed", sa.Integer, nullable=False, server_default="0"))
    op.add_column("user", sa.Column("pin_attempts", sa.Integer, nullable=False, server_default="0"))
    op.add_column("user", sa.Column("pin_locked_until", sa.Integer, nullable=True))

    # 3. Delete all existing users (personal project - fresh start)
    op.execute("DELETE FROM transaction_tag")
    op.execute("DELETE FROM transaction")
    op.execute("DELETE FROM category")
    op.execute("DELETE FROM tag")
    op.execute("DELETE FROM user")

    # 4. Insert 2 preset users with default PIN "1234"
    # bcrypt hash of "1234": $2b$12$LJ3m4ys3Lk0TSwHjnF4oR.K3VJxqfVYqxSy3TqFG3YfP1y7rP3hAa
    # Using a pre-computed hash for "1234"
    import bcrypt
    pin_hash = bcrypt.hashpw(b"1234", bcrypt.gensalt()).decode("utf-8")

    import time
    now = int(time.time())

    op.execute(f"""
        INSERT INTO user (username, password, nickname, pin_changed, pin_attempts, created_at, updated_at)
        VALUES
            ('user1', '{pin_hash}', '用户1', 0, 0, {now}, {now}),
            ('user2', '{pin_hash}', '用户2', 0, 0, {now}, {now})
    """)

    # 5. Create preset categories for each user
    preset_categories = [
        ("餐饮", "🍽️", "#FF5722"),
        ("交通", "🚗", "#2196F3"),
        ("购物", "🛒", "#FF9800"),
        ("住房", "🏠", "#795548"),
        ("娱乐", "🎮", "#9C27B0"),
        ("医疗", "💊", "#4CAF50"),
        ("教育", "📚", "#009688"),
        ("其他", "📦", "#607D8B"),
    ]

    # Get user IDs
    conn = op.get_bind()
    result = conn.execute(sa.text("SELECT id FROM user ORDER BY id"))
    user_ids = [row[0] for row in result]

    for uid in user_ids:
        for i, (name, icon, color) in enumerate(preset_categories):
            op.execute(f"""
                INSERT INTO category (uid, name, icon, color, display_order, created_at, updated_at)
                VALUES ({uid}, '{name}', '{icon}', '{color}', {i}, {now}, {now})
            """)


def downgrade() -> None:
    # Remove preset data
    op.execute("DELETE FROM category")
    op.execute("DELETE FROM user")

    # Remove PIN columns
    op.drop_column("user", "pin_locked_until")
    op.drop_column("user", "pin_attempts")
    op.drop_column("user", "pin_changed")

    # Add back email column
    op.add_column("user", sa.Column("email", sa.String(128), nullable=False, server_default=""))
