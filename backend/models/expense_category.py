import time
from sqlalchemy import Integer, String, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column
from database import Base


class ExpenseCategory(Base):
    __tablename__ = "expense_category"
    __table_args__ = (
        Index("idx_category_uid_deleted", "uid", "deleted", "display_order"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uid: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(32), nullable=False)
    icon: Mapped[str] = mapped_column(String(10), nullable=False, default="📦")
    color: Mapped[str] = mapped_column(String(7), nullable=False, default="#607D8B")
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    deleted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[int] = mapped_column(Integer, nullable=False, default=lambda: int(time.time()))
    updated_at: Mapped[int] = mapped_column(Integer, nullable=False, default=lambda: int(time.time()))
    deleted_at: Mapped[int] = mapped_column(Integer, default=0)
