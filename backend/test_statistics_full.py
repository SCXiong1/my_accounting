"""statistics_service 单元测试：overview / by_category / by_tag"""
from datetime import datetime
import time

import pytest

from constants import APP_TIMEZONE
from models.transaction import Transaction
from models.transaction_tag import TransactionTag
from models.user import User
from services.statistics_service import by_category, by_tag, overview
from utils.security import hash_pin

pytest_plugins = ["conftest_unit"]


# ─── helpers ───

async def _create_user(db, username):
    now = int(time.time())
    user = User(
        username=username,
        password=hash_pin("1234"),
        nickname=username,
        pin_changed=1,
        created_at=now,
        updated_at=now,
    )
    db.add(user)
    await db.flush()
    return user


async def _add_txn(db, uid, cat_id, amount, ts, tag_ids=None, deleted=False):
    """Seed a transaction (optionally soft-deleted) and return the model."""
    t = Transaction(
        uid=uid, amount=amount, category_id=cat_id,
        transaction_time=ts, created_at=ts, updated_at=ts,
        deleted=1 if deleted else 0, deleted_at=ts if deleted else 0,
    )
    db.add(t)
    await db.flush()
    if tag_ids:
        for tid in tag_ids:
            db.add(TransactionTag(uid=uid, transaction_id=t.id, tag_id=tid, created_at=ts))
        await db.flush()
    return t


# ─── overview tests ───

@pytest.mark.asyncio
async def test_overview_returns_today_week_month_year_totals(db, state):
    """overview 返回 today/week/month/year 总额"""
    now = datetime.now(APP_TIMEZONE)
    today_start = int(now.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
    ts = today_start + 3600  # 01:00 today — within all 4 periods

    before = await overview(db, state.uid)
    await _add_txn(db, state.uid, state.cat_ids[0], 9999, ts)
    await db.commit()

    after = await overview(db, state.uid)
    assert after.today - before.today == 9999
    assert after.this_week - before.this_week == 9999
    assert after.this_month - before.this_month == 9999
    assert after.this_year - before.this_year == 9999


@pytest.mark.asyncio
async def test_overview_returns_zeros_when_no_transactions(db):
    """没有交易时返回全零"""
    user = await _create_user(db, "overview_empty_user")
    await db.commit()

    result = await overview(db, user.id)
    assert result.today == 0
    assert result.this_week == 0
    assert result.this_month == 0
    assert result.this_year == 0


@pytest.mark.asyncio
async def test_overview_only_counts_current_user(db, state):
    """overview 只统计当前用户的交易"""
    other = await _create_user(db, "overview_other_user")
    now_ts = int(datetime.now(APP_TIMEZONE).timestamp())
    await _add_txn(db, other.id, state.cat_ids[0], 55555, now_ts)
    await db.commit()

    before = await overview(db, state.uid)
    await _add_txn(db, state.uid, state.cat_ids[0], 1111, now_ts)
    await db.commit()

    after = await overview(db, state.uid)
    # Other user's 55555 should not leak in
    assert after.today - before.today == 1111


@pytest.mark.asyncio
async def test_overview_excludes_deleted_transactions(db, state):
    """overview 不包含已软删除的交易"""
    now = datetime.now(APP_TIMEZONE)
    today_start = int(now.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
    ts = today_start + 1800

    before = await overview(db, state.uid)
    await _add_txn(db, state.uid, state.cat_ids[0], 7777, ts, deleted=True)
    await db.commit()

    after = await overview(db, state.uid)
    assert after.today == before.today
    assert after.this_month == before.this_month


# ─── by_category tests ───

@pytest.mark.asyncio
async def test_by_category_groups_correctly(db, state):
    """by_category 按分类正确分组"""
    ts_base = 1672531200  # 2023-01-01 00:00:00 UTC
    await _add_txn(db, state.uid, state.cat_ids[0], 4000, ts_base)
    await _add_txn(db, state.uid, state.cat_ids[0], 6000, ts_base + 1)
    await _add_txn(db, state.uid, state.cat_ids[1], 3000, ts_base + 2)
    await db.commit()

    result = await by_category(db, state.uid, start_time=ts_base, end_time=ts_base + 10)
    cat_totals = {item.category_id: item.total_amount for item in result}
    assert cat_totals[state.cat_ids[0]] == 10000
    assert cat_totals[state.cat_ids[1]] == 3000


@pytest.mark.asyncio
async def test_by_category_calculates_percentages(db, state):
    """by_category 百分比计算正确"""
    ts_base = 1672617600  # 2023-01-02
    await _add_txn(db, state.uid, state.cat_ids[0], 7500, ts_base)
    await _add_txn(db, state.uid, state.cat_ids[1], 2500, ts_base + 1)
    await db.commit()

    result = await by_category(db, state.uid, start_time=ts_base, end_time=ts_base + 10)
    pct_map = {item.category_id: item.percentage for item in result}
    assert pct_map[state.cat_ids[0]] == 75.0
    assert pct_map[state.cat_ids[1]] == 25.0


@pytest.mark.asyncio
async def test_by_category_respects_time_range(db, state):
    """by_category 尊重时间范围过滤"""
    ts_in = 1672704000   # 2023-01-03
    ts_out = 1672790400  # 2023-01-04
    await _add_txn(db, state.uid, state.cat_ids[0], 5000, ts_in)
    await _add_txn(db, state.uid, state.cat_ids[0], 9000, ts_out)
    await db.commit()

    result = await by_category(db, state.uid, start_time=ts_in, end_time=ts_in + 100)
    total = sum(item.total_amount for item in result)
    assert total == 5000


@pytest.mark.asyncio
async def test_by_category_respects_tag_filter(db, state):
    """by_category 尊重标签过滤"""
    ts_base = 1672876800  # 2023-01-05
    await _add_txn(db, state.uid, state.cat_ids[0], 3000, ts_base, tag_ids=[state.tag_ids[0]])
    await _add_txn(db, state.uid, state.cat_ids[0], 7000, ts_base + 1)
    await db.commit()

    result = await by_category(
        db, state.uid, start_time=ts_base, end_time=ts_base + 10, tag_ids=[state.tag_ids[0]],
    )
    total = sum(item.total_amount for item in result)
    assert total == 3000


@pytest.mark.asyncio
async def test_by_category_returns_empty_when_no_transactions(db, state):
    """无交易时返回空列表"""
    result = await by_category(db, state.uid, start_time=1000000, end_time=1000010)
    assert result == []


# ─── by_tag tests ───

@pytest.mark.asyncio
async def test_by_tag_groups_correctly(db, state):
    """by_tag 按标签正确分组"""
    ts_base = 1672963200  # 2023-01-06
    await _add_txn(db, state.uid, state.cat_ids[0], 4000, ts_base, tag_ids=[state.tag_ids[0]])
    await _add_txn(db, state.uid, state.cat_ids[0], 6000, ts_base + 1, tag_ids=[state.tag_ids[0]])
    await _add_txn(db, state.uid, state.cat_ids[0], 3000, ts_base + 2, tag_ids=[state.tag_ids[1]])
    await db.commit()

    result = await by_tag(db, state.uid, start_time=ts_base, end_time=ts_base + 10)
    tag_totals = {item.tag_id: item.total_amount for item in result}
    assert tag_totals[state.tag_ids[0]] == 10000
    assert tag_totals[state.tag_ids[1]] == 3000


@pytest.mark.asyncio
async def test_by_tag_calculates_percentages(db, state):
    """by_tag 百分比计算正确"""
    ts_base = 1673049600  # 2023-01-07
    await _add_txn(db, state.uid, state.cat_ids[0], 8000, ts_base, tag_ids=[state.tag_ids[0]])
    await _add_txn(db, state.uid, state.cat_ids[0], 2000, ts_base + 1, tag_ids=[state.tag_ids[1]])
    await db.commit()

    result = await by_tag(db, state.uid, start_time=ts_base, end_time=ts_base + 10)
    pct_map = {item.tag_id: item.percentage for item in result}
    assert pct_map[state.tag_ids[0]] == 80.0
    assert pct_map[state.tag_ids[1]] == 20.0


@pytest.mark.asyncio
async def test_by_tag_respects_time_range(db, state):
    """by_tag 尊重时间范围过滤"""
    ts_in = 1673136000   # 2023-01-08
    ts_out = 1673222400  # 2023-01-09
    await _add_txn(db, state.uid, state.cat_ids[0], 5000, ts_in, tag_ids=[state.tag_ids[0]])
    await _add_txn(db, state.uid, state.cat_ids[0], 9000, ts_out, tag_ids=[state.tag_ids[0]])
    await db.commit()

    result = await by_tag(db, state.uid, start_time=ts_in, end_time=ts_in + 100)
    total = sum(item.total_amount for item in result)
    assert total == 5000


@pytest.mark.asyncio
async def test_by_tag_respects_category_filter(db, state):
    """by_tag 尊重分类过滤"""
    ts_base = 1673308800  # 2023-01-10
    await _add_txn(db, state.uid, state.cat_ids[0], 3000, ts_base, tag_ids=[state.tag_ids[0]])
    await _add_txn(db, state.uid, state.cat_ids[1], 7000, ts_base + 1, tag_ids=[state.tag_ids[0]])
    await db.commit()

    result = await by_tag(
        db, state.uid, start_time=ts_base, end_time=ts_base + 10, category_ids=[state.cat_ids[0]],
    )
    total = sum(item.total_amount for item in result)
    assert total == 3000
