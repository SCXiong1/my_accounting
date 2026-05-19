from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from database import Base
from models.mixins import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    password: Mapped[str] = mapped_column(String(60), nullable=False)  # bcrypt hash
    nickname: Mapped[str] = mapped_column(String(64), nullable=False, default="")
