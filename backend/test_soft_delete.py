"""ExpenseTagIndex 软删除行为测试 —— 直接对内存 SQLite 测试 service 层"""
import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from database import Base
from services.expense_service import create_expense, update_expense, delete_expense, restore_expense, get_expense
from schemas.expense import ExpenseCreate, ExpenseUpdate
from models.expense_tag_index import ExpenseTagIndex
from models.expense_category import ExpenseCategory
from models.expense_tag import ExpenseTag
from models.user import User
from utils.security import hash_password
from sqlalchemy import select

TEST_DB = "sqlite+aiosqlite://"


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


async def _setup_db():
    """模块级：创建表 + 种子数据，返回 engine 和各 ID"""
    engine = create_async_engine(TEST_DB)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        async with session.begin():
            user = User(username="test_softdel", email="t@t.com",
                        password=hash_password("123456"))
            session.add(user)
            await session.flush()
            uid = user.id

            cat = ExpenseCategory(uid=uid, name="餐饮", icon="A", color="#F00", display_order=1)
            session.add(cat)
            await session.flush()
            cat_id = cat.id

            tags = [
                ExpenseTag(uid=uid, name="午餐", display_order=1),
                ExpenseTag(uid=uid, name="晚餐", display_order=2),
                ExpenseTag(uid=uid, name="外卖", display_order=3),
            ]
            for t in tags:
                session.add(t)
            await session.flush()
            tag_ids = [t.id for t in tags]

    return engine, uid, cat_id, tag_ids


# 用 fixture 包装异步初始化
class _State:
    engine = None
    uid = 0
    cat_id = 0
    tag_ids = []


@pytest.fixture(scope="module")
def state(event_loop):
    s = _State()
    engine, uid, cat_id, tag_ids = event_loop.run_until_complete(_setup_db())
    s.engine = engine
    s.uid = uid
    s.cat_id = cat_id
    s.tag_ids = tag_ids
    yield s
    async def _cleanup():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()
    event_loop.run_until_complete(_cleanup())


@pytest.fixture
def db(event_loop, state):
    """每个测试独立的 session（自动 commit）"""
    session_factory = async_sessionmaker(state.engine, class_=AsyncSession, expire_on_commit=False)
    async def _make():
        return session_factory()
    return event_loop.run_until_complete(_make())


@pytest.mark.asyncio
async def test_update_soft_deletes_old_tags(db, state):
    """更新标签时，旧关联 soft-delete，新关联 active"""
    req = ExpenseCreate(
        amount=5000, category_id=state.cat_id, tag_ids=state.tag_ids[:2], transaction_time=1700000000)
    expense = await create_expense(db, state.uid, req)

    update_req = ExpenseUpdate(tag_ids=[state.tag_ids[2]])
    await update_expense(db, state.uid, expense.id, update_req)

    result = await db.execute(
        select(ExpenseTagIndex).where(ExpenseTagIndex.expense_id == expense.id))
    rows = result.scalars().all()

    assert len(rows) == 3, f"期望 3 行，实际 {len(rows)}"
    old_rows = [r for r in rows if r.tag_id in state.tag_ids[:2]]
    new_rows = [r for r in rows if r.tag_id == state.tag_ids[2]]
    assert len(old_rows) == 2
    assert all(r.deleted == 1 for r in old_rows), "旧关联应为 deleted=1"
    assert len(new_rows) == 1
    assert new_rows[0].deleted == 0, "新关联应为 deleted=0"


@pytest.mark.asyncio
async def test_delete_soft_deletes_tag_associations(db, state):
    """删除支出时同步 soft-delete 标签关联"""
    req = ExpenseCreate(
        amount=5000, category_id=state.cat_id, tag_ids=state.tag_ids[:1], transaction_time=1700000000)
    expense = await create_expense(db, state.uid, req)

    await delete_expense(db, state.uid, expense.id)

    result = await db.execute(
        select(ExpenseTagIndex).where(ExpenseTagIndex.expense_id == expense.id))
    rows = result.scalars().all()
    assert len(rows) == 1
    assert rows[0].deleted == 1, "删除支出后标签关联应为 deleted=1"


@pytest.mark.asyncio
async def test_restore_recovers_tag_associations(db, state):
    """恢复支出时标签关联也恢复"""
    req = ExpenseCreate(
        amount=5000, category_id=state.cat_id, tag_ids=state.tag_ids[:1], transaction_time=1700000000)
    expense = await create_expense(db, state.uid, req)

    await delete_expense(db, state.uid, expense.id)
    await restore_expense(db, state.uid, expense.id)

    restored = await get_expense(db, state.uid, expense.id)
    assert len(restored.tags) == 1
    assert restored.tags[0].id == state.tag_ids[0]
