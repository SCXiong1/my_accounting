from sqlalchemy import Integer, String, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column
from database import Base
from models.mixins import TimestampMixin, SoftDeleteMixin


class ExpenseTag(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "expense_tag"
    __table_args__ = (
        Index("idx_tag_uid_deleted", "uid", "deleted", "display_order"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uid: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(32), nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
