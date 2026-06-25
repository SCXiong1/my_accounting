"""statistics_service 聚合行为测试"""
import pytest

from models.transaction import Transaction
from models.transaction_tag import TransactionTag
from services.statistics_service import monthly

pytest_plugins = ["conftest_unit"]


@pytest.mark.asyncio
async def test_monthly_category_aggregation(db, state):
    """monthly 按分类聚合金额正确"""
    # 用固定月份 2024-03 避免与其他测试重叠
    ts = 1709280000  # 2024-03-01 16:00:00 UTC

    e1 = Transaction(uid=state.uid, amount=5000, category_id=state.cat_ids[0],
                 transaction_time=ts, created_at=ts, updated_at=ts)
    e2 = Transaction(uid=state.uid, amount=3000, category_id=state.cat_ids[0],
                 transaction_time=ts + 3600, created_at=ts, updated_at=ts)
    db.add(e1)
    db.add(e2)
    await db.flush()

    db.add(TransactionTag(uid=state.uid, transaction_id=e1.id, tag_id=state.tag_ids[0], created_at=ts))
    db.add(TransactionTag(uid=state.uid, transaction_id=e2.id, tag_id=state.tag_ids[1], created_at=ts))
    await db.commit()

    result = await monthly(db, state.uid, start_year=2024, start_month=3, end_year=2024, end_month=3)

    assert len(result) == 1
    m = result[0]
    assert m.year == 2024
    assert m.month == 3
    assert m.total_amount == 8000
    assert m.transaction_count == 2
    assert len(m.by_category) == 1
    assert m.by_category[0].category_id == state.cat_ids[0]
    assert m.by_category[0].amount == 8000


@pytest.mark.asyncio
async def test_monthly_tag_aggregation(db, state):
    """monthly 按标签聚合金额正确"""
    # 用固定月份 2024-04 避免与其他测试重叠
    ts = 1711929600  # 2024-04-01 00:00:00 UTC

    e1 = Transaction(uid=state.uid, amount=5000, category_id=state.cat_ids[0],
                 transaction_time=ts, created_at=ts, updated_at=ts)
    e2 = Transaction(uid=state.uid, amount=3000, category_id=state.cat_ids[0],
                 transaction_time=ts + 3600, created_at=ts, updated_at=ts)
    db.add(e1)
    db.add(e2)
    await db.flush()

    db.add(TransactionTag(uid=state.uid, transaction_id=e1.id, tag_id=state.tag_ids[0], created_at=ts))
    db.add(TransactionTag(uid=state.uid, transaction_id=e2.id, tag_id=state.tag_ids[1], created_at=ts))
    await db.commit()

    result = await monthly(db, state.uid, start_year=2024, start_month=4, end_year=2024, end_month=4)

    assert len(result) == 1
    m = result[0]
    assert len(m.by_tag) == 2
    tag_amounts = {t.tag_id: t.amount for t in m.by_tag}
    assert tag_amounts[state.tag_ids[0]] == 5000
    assert tag_amounts[state.tag_ids[1]] == 3000
