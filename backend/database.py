from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from config import get

DATABASE_PATH = get("database.path")
DATABASE_URL = f"sqlite+aiosqlite:///{DATABASE_PATH}"

engine = create_async_engine(DATABASE_URL, echo=False)

# 每个连接启用外键约束
@event.listens_for(engine.sync_engine, "connect")
def _set_sqlite_pragma(dbapi_connection: Any, _connection_record: Any) -> None:
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.close()

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def init_db() -> None:
    import os
    os.makedirs(os.path.dirname(DATABASE_PATH) or ".", exist_ok=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.exec_driver_sql("PRAGMA foreign_keys = ON")
