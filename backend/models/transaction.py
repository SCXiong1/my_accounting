from sqlalchemy import ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base
from models.mixins import SoftDeleteMixin, TimestampMixin


class Transaction(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "transaction"
    __table_args__ = (
        Index("idx_transaction_uid_deleted_time", "uid", "deleted", "transaction_time"),
        Index("idx_transaction_uid_deleted_category", "uid", "deleted", "category_id", "transaction_time"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uid: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("category.id"), nullable=False)
    transaction_time: Mapped[int] = mapped_column(Integer, nullable=False)
    timezone_offset: Mapped[int] = mapped_column(Integer, nullable=False, default=480)  # UTC+8 in minutes
    note: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    type: Mapped[str] = mapped_column(String(7), nullable=False, default="expense")
