import time

from sqlalchemy import ForeignKey, Index, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class TransactionTag(Base):
    __tablename__ = "transaction_tag"
    __table_args__ = (
        UniqueConstraint("transaction_id", "tag_id"),
        Index("idx_tag_index_uid_tag", "uid", "tag_id", "transaction_id"),
        Index("idx_tag_index_transaction", "transaction_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uid: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    transaction_id: Mapped[int] = mapped_column(Integer, ForeignKey("transaction.id"), nullable=False)
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey("tag.id"), nullable=False)
    created_at: Mapped[int] = mapped_column(Integer, nullable=False, default=lambda: int(time.time()))
