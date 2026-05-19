import time
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column


class TimestampMixin:
    created_at: Mapped[int] = mapped_column(Integer, nullable=False, default=lambda: int(time.time()))
    updated_at: Mapped[int] = mapped_column(Integer, nullable=False, default=lambda: int(time.time()))


class SoftDeleteMixin:
    deleted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    deleted_at: Mapped[int] = mapped_column(Integer, default=0)
