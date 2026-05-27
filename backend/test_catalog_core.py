"""catalog_core 泛型 CRUD 辅助函数测试"""
import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from database import Base
from models.expense_category import ExpenseCategory
from models.user import User
from utils.security import hash_password
from middleware.error_handler import NotFoundException

TEST_DB = "sqlite+aiosqlite://"


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


class _State:
    engine = None
    uid = 0
    cat_ids = []


@pytest.fixture(scope="module")
def state(event_loop):
    s = _State()
    async def _init():
        s.engine = create_async_engine(TEST_DB)
        async with s.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        session_factory = async_sessionmaker(s.engine, class_=AsyncSession, expire_on_commit=False)
        async with session_factory() as session:
            async with session.begin():
                user = User(username="test_cat", email="t@t.com", password=hash_password("123456"))
                session.add(user)
                await session.flush()
                s.uid = user.id

                cats = [ExpenseCategory(uid=s.uid, name="A", display_order=1),
                        ExpenseCategory(uid=s.uid, name="B", display_order=2)]
                for c in cats:
                    session.add(c)
                await session.flush()
                s.cat_ids = [c.id for c in cats]

    event_loop.run_until_complete(_init())
    yield s
    async def _clean():
        async with s.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await s.engine.dispose()
    event_loop.run_until_complete(_clean())


@pytest.fixture
def db(event_loop, state):
    """每个测试独立 session"""
    session_factory = async_sessionmaker(state.engine, class_=AsyncSession, expire_on_commit=False)
    async def _make():
        return session_factory()
    return event_loop.run_until_complete(_make())


@pytest.mark.asyncio
async def test_find_or_404_found(db, state):
    """找到时返回 model 实例"""
    from services.catalog_core import find_or_404
    cat = await find_or_404(db, state.uid, ExpenseCategory, state.cat_ids[0], "分类")
    assert cat is not None
    assert cat.id == state.cat_ids[0]
    assert cat.name == "A"


@pytest.mark.asyncio
async def test_find_or_404_raises(db, state):
    """未找到时抛出 NotFoundException"""
    from services.catalog_core import find_or_404
    with pytest.raises(NotFoundException):
        await find_or_404(db, state.uid, ExpenseCategory, 99999, "分类")


@pytest.mark.asyncio
async def test_soft_delete(db, state):
    """soft_delete 设置 deleted=1 并返回 dict"""
    from services.catalog_core import soft_delete
    result = await soft_delete(db, state.uid, ExpenseCategory, state.cat_ids[0], "分类")
    assert result == {"deleted": True}

    # 验证 DB 状态
    from sqlalchemy import select
    r = await db.execute(select(ExpenseCategory).where(ExpenseCategory.id == state.cat_ids[0]))
    cat = r.scalar_one()
    assert cat.deleted == 1


@pytest.mark.asyncio
async def test_sort_models(db, state):
    """sort_models 批量更新 display_order 并返回排序列表"""
    from services.catalog_core import sort_models

    # 创建测试专用的分类（避免其他测试的副作用）
    import time
    now = int(time.time())
    c1 = ExpenseCategory(uid=state.uid, name="sort1", display_order=5, created_at=now, updated_at=now)
    c2 = ExpenseCategory(uid=state.uid, name="sort2", display_order=2, created_at=now, updated_at=now)
    db.add(c1)
    db.add(c2)
    await db.flush()

    orders = [
        {"id": c2.id, "display_order": 50},
        {"id": c1.id, "display_order": 10},
    ]
    result = await sort_models(db, state.uid, ExpenseCategory, orders)

    assert len(result) >= 2
    ids = [c.id for c in result]
    # c1(display_order=10) 应在 c2(50) 前面
    assert ids.index(c1.id) < ids.index(c2.id), "display_order=10 应在 50 前面"
