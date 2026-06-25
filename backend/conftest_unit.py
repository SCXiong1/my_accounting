"""Shared fixtures for backend unit tests."""
import asyncio
import time
from collections.abc import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from database import Base
from models.category import Category
from models.tag import Tag
from models.user import User
from utils.security import hash_pin

TEST_DB = "sqlite+aiosqlite://"


class State:
    def __init__(self) -> None:
        self.engine: AsyncEngine | None = None
        self.uid: int = 0
        self.cat_ids: list[int] = []
        self.tag_ids: list[int] = []


@pytest.fixture(scope="module")
def event_loop() -> Generator[asyncio.AbstractEventLoop]:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="module")
async def state() -> AsyncGenerator[State]:
    s = State()
    s.engine = create_async_engine(
        TEST_DB,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with s.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(s.engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        async with session.begin():
            now = int(time.time())
            user = User(
                username="test_shared",
                password=hash_pin("1234"),
                nickname="测试用户",
                pin_changed=1,
                created_at=now,
                updated_at=now,
            )
            session.add(user)
            await session.flush()
            s.uid = user.id

            cats = [
                Category(uid=s.uid, name="餐饮", display_order=1),
                Category(uid=s.uid, name="交通", display_order=2),
                Category(uid=s.uid, name="空分类", display_order=3),
            ]
            for c in cats:
                session.add(c)
            await session.flush()
            s.cat_ids = [c.id for c in cats]

            tags = [
                Tag(uid=s.uid, name="午餐", display_order=1),
                Tag(uid=s.uid, name="晚餐", display_order=2),
                Tag(uid=s.uid, name="外卖", display_order=3),
            ]
            for t in tags:
                session.add(t)
            await session.flush()
            s.tag_ids = [t.id for t in tags]

    yield s

    async with s.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await s.engine.dispose()


@pytest_asyncio.fixture
async def db(state: State) -> AsyncGenerator[AsyncSession]:
    session_factory = async_sessionmaker(state.engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
