from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base
from models.mixins import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(60), nullable=False)  # bcrypt hash
    nickname: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    pin_changed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    pin_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    pin_locked_until: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
