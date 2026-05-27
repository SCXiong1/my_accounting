"""statistics_service 聚合行为测试"""
import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from database import Base
from services.statistics_service import monthly, by_category, by_tag
from models.expense_category import ExpenseCategory
from models.expense_tag import ExpenseTag
from models.expense_tag_index import ExpenseTagIndex
from models.expense import Expense
from models.user import User
from utils.security import hash_password

TEST_DB = "sqlite+aiosqlite://"


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


class _State:
    engine = None
    uid = 0
    cat_id = 0
    tag_ids = []


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
                user = User(username="test_stat", email="t@t.com", password=hash_password("123456"))
                session.add(user)
                await session.flush()
                s.uid = user.id

                cat = ExpenseCategory(uid=s.uid, name="餐饮", icon="A", color="#F00", display_order=1)
                session.add(cat)
                await session.flush()
                s.cat_id = cat.id

                tags = [ExpenseTag(uid=s.uid, name="午餐", display_order=1),
                        ExpenseTag(uid=s.uid, name="外卖", display_order=2)]
                for t in tags:
                    session.add(t)
                await session.flush()
                s.tag_ids = [t.id for t in tags]

    event_loop.run_until_complete(_init())
    yield s
    async def _clean():
        async with s.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await s.engine.dispose()
    event_loop.run_until_complete(_clean())


@pytest.fixture
def db(event_loop, state):
    session_factory = async_sessionmaker(state.engine, class_=AsyncSession, expire_on_commit=False)
    async def _make():
        return session_factory()
    return event_loop.run_until_complete(_make())


@pytest.mark.asyncio
async def test_monthly_category_aggregation(db, state):
    """monthly 按分类聚合金额正确"""
    # 用固定月份 2024-03 避免与其他测试重叠
    ts = 1709280000  # 2024-03-01 16:00:00 UTC

    e1 = Expense(uid=state.uid, amount=5000, category_id=state.cat_id,
                 transaction_time=ts, created_at=ts, updated_at=ts)
    e2 = Expense(uid=state.uid, amount=3000, category_id=state.cat_id,
                 transaction_time=ts + 3600, created_at=ts, updated_at=ts)
    db.add(e1)
    db.add(e2)
    await db.flush()

    db.add(ExpenseTagIndex(uid=state.uid, expense_id=e1.id, tag_id=state.tag_ids[0], created_at=ts))
    db.add(ExpenseTagIndex(uid=state.uid, expense_id=e2.id, tag_id=state.tag_ids[1], created_at=ts))
    await db.commit()

    result = await monthly(db, state.uid, start_year=2024, start_month=3, end_year=2024, end_month=3)

    assert len(result) == 1
    m = result[0]
    assert m.year == 2024
    assert m.month == 3
    assert m.total_amount == 8000
    assert m.transaction_count == 2
    assert len(m.by_category) == 1
    assert m.by_category[0].category_id == state.cat_id
    assert m.by_category[0].amount == 8000


@pytest.mark.asyncio
async def test_monthly_tag_aggregation(db, state):
    """monthly 按标签聚合金额正确"""
    # 用固定月份 2024-04 避免与其他测试重叠
    ts = 1711929600  # 2024-04-01 00:00:00 UTC

    e1 = Expense(uid=state.uid, amount=5000, category_id=state.cat_id,
                 transaction_time=ts, created_at=ts, updated_at=ts)
    e2 = Expense(uid=state.uid, amount=3000, category_id=state.cat_id,
                 transaction_time=ts + 3600, created_at=ts, updated_at=ts)
    db.add(e1)
    db.add(e2)
    await db.flush()

    db.add(ExpenseTagIndex(uid=state.uid, expense_id=e1.id, tag_id=state.tag_ids[0], created_at=ts))
    db.add(ExpenseTagIndex(uid=state.uid, expense_id=e2.id, tag_id=state.tag_ids[1], created_at=ts))
    await db.commit()

    result = await monthly(db, state.uid, start_year=2024, start_month=4, end_year=2024, end_month=4)

    assert len(result) == 1
    m = result[0]
    assert len(m.by_tag) == 2
    tag_amounts = {t.tag_id: t.amount for t in m.by_tag}
    assert tag_amounts[state.tag_ids[0]] == 5000
    assert tag_amounts[state.tag_ids[1]] == 3000
