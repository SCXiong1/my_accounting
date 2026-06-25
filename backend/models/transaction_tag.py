import time
from sqlalchemy import Integer, UniqueConstraint, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column
from database import Base


class ExpenseTagIndex(Base):
    __tablename__ = "expense_tag_index"
    __table_args__ = (
        UniqueConstraint("expense_id", "tag_id"),
        Index("idx_tag_index_uid_tag", "uid", "tag_id", "expense_id"),
        Index("idx_tag_index_expense", "expense_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uid: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    expense_id: Mapped[int] = mapped_column(Integer, ForeignKey("expense.id"), nullable=False)
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey("expense_tag.id"), nullable=False)
    created_at: Mapped[int] = mapped_column(Integer, nullable=False, default=lambda: int(time.time()))
    deleted: Mapped[int] = mapped_column(Integer, nullable=False, default=0, index=True)
    deleted_at: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
