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
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        await conn.exec_driver_sql("PRAGMA foreign_keys = ON")

    await _seed_preset_data()


async def _seed_preset_data() -> None:
    import time
    from sqlalchemy import select
    from models.user import User
    from models.category import Category
    from utils.security import hash_pin

    async with async_session() as session:
        result = await session.execute(select(User).limit(1))
        if result.scalar_one_or_none() is not None:
            return

        now = int(time.time())
        pin_hash = hash_pin("1234")

        user1 = User(
            username="user1",
            password=pin_hash,
            nickname="用户1",
            pin_changed=0,
            created_at=now,
            updated_at=now,
        )
        user2 = User(
            username="user2",
            password=pin_hash,
            nickname="用户2",
            pin_changed=0,
            created_at=now,
            updated_at=now,
        )
        session.add_all([user1, user2])
        await session.flush()

        preset_categories = [
            ("餐饮", "🍽️", "#FF5722"),
            ("交通", "🚗", "#2196F3"),
            ("购物", "🛒", "#FF9800"),
            ("住房", "🏠", "#795548"),
            ("娱乐", "🎮", "#9C27B0"),
            ("医疗", "💊", "#4CAF50"),
            ("教育", "📚", "#009688"),
            ("其他", "📦", "#607D8B"),
        ]

        for user in [user1, user2]:
            for i, (name, icon, color) in enumerate(preset_categories):
                session.add(Category(
                    uid=user.id,
                    name=name,
                    icon=icon,
                    color=color,
                    display_order=i,
                    created_at=now,
                    updated_at=now,
                ))

        await session.commit()
