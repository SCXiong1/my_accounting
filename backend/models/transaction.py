from sqlalchemy import Integer, String, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column
from database import Base
from models.mixins import TimestampMixin, SoftDeleteMixin


class Expense(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "expense"
    __table_args__ = (
        Index("idx_expense_uid_deleted_time", "uid", "deleted", "transaction_time"),
        Index("idx_expense_uid_deleted_category", "uid", "deleted", "category_id", "transaction_time"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uid: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("expense_category.id"), nullable=False)
    transaction_time: Mapped[int] = mapped_column(Integer, nullable=False)
    timezone_offset: Mapped[int] = mapped_column(Integer, nullable=False, default=480)
    note: Mapped[str] = mapped_column(String(255), nullable=False, default="")
