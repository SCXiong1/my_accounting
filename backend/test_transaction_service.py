"""transaction_service 单元测试：_apply_keyword + permanent_delete_transactions"""
import time

import pytest
from sqlalchemy import select

from models.transaction import Transaction
from models.transaction_tag import TransactionTag
from models.user import User
from services.transaction_service import _apply_keyword, permanent_delete_transactions
from utils.security import hash_password

pytest_plugins = ["conftest_unit"]


# ─── helpers ───

def _base_query(uid: int):
    """Non-deleted transactions for user."""
    return select(Transaction).where(Transaction.uid == uid, Transaction.deleted == 0)


async def _add_transaction(db, state, *, amount=5000, cat_id=None, tag_ids=None, note="", ts=None):
    """Create and flush a transaction, return the model instance."""
    if cat_id is None:
        cat_id = state.cat_ids[0]
    if ts is None:
        ts = int(time.time())
    t = Transaction(
        uid=state.uid, amount=amount, category_id=cat_id,
        transaction_time=ts, note=note, created_at=ts, updated_at=ts,
    )
    db.add(t)
    await db.flush()
    if tag_ids:
        for tid in tag_ids:
            db.add(TransactionTag(uid=state.uid, transaction_id=t.id, tag_id=tid, created_at=ts))
        await db.flush()
    return t


# ─── _apply_keyword tests ───

@pytest.mark.asyncio
async def test_keyword_matches_note(db, state):
    """keyword 匹配交易备注"""
    t = await _add_transaction(db, state, note="午饭报销abc", ts=1690000100)
    await db.commit()

    query = _apply_keyword(_base_query(state.uid), "午饭报销abc", state.uid)
    result = await db.execute(query)
    ids = [r.id for r in result.scalars().all()]
    assert t.id in ids


@pytest.mark.asyncio
async def test_keyword_matches_category_name(db, state):
    """keyword 匹配分类名称"""
    # state.cat_ids[1] = "交通"
    t = await _add_transaction(db, state, cat_id=state.cat_ids[1], ts=1690000200)
    await db.commit()

    query = _apply_keyword(_base_query(state.uid), "交通", state.uid)
    result = await db.execute(query)
    ids = [r.id for r in result.scalars().all()]
    assert t.id in ids


@pytest.mark.asyncio
async def test_keyword_matches_tag_name(db, state):
    """keyword 匹配标签名称"""
    # state.tag_ids[0] = "午餐"
    t = await _add_transaction(db, state, tag_ids=[state.tag_ids[0]], ts=1690000300)
    await db.commit()

    query = _apply_keyword(_base_query(state.uid), "午餐", state.uid)
    result = await db.execute(query)
    ids = [r.id for r in result.scalars().all()]
    assert t.id in ids


@pytest.mark.asyncio
async def test_keyword_matches_amount(db, state):
    """keyword 为纯数字时匹配金额"""
    t = await _add_transaction(db, state, amount=12345, ts=1690000400)
    await db.commit()

    query = _apply_keyword(_base_query(state.uid), "12345", state.uid)
    result = await db.execute(query)
    ids = [r.id for r in result.scalars().all()]
    assert t.id in ids


@pytest.mark.asyncio
async def test_empty_keyword_returns_all(db, state):
    """None 或空字符串关键词不做任何过滤"""
    t1 = await _add_transaction(db, state, note="kw_none_a", ts=1690000500)
    t2 = await _add_transaction(db, state, note="kw_none_b", ts=1690000501)
    await db.commit()

    # None → no filter added
    query = _apply_keyword(_base_query(state.uid), None, state.uid)
    result = await db.execute(query)
    ids = {r.id for r in result.scalars().all()}
    assert t1.id in ids
    assert t2.id in ids

    # Empty string → no filter added
    query2 = _apply_keyword(_base_query(state.uid), "", state.uid)
    result2 = await db.execute(query2)
    ids2 = {r.id for r in result2.scalars().all()}
    assert t1.id in ids2
    assert t2.id in ids2


@pytest.mark.asyncio
async def test_keyword_no_match_returns_empty(db, state):
    """无匹配关键词返回空列表"""
    await _add_transaction(db, state, note="确定不会匹配xyz999", ts=1690000600)
    await db.commit()

    query = _apply_keyword(_base_query(state.uid), "绝对不存在的关键词_qwerty", state.uid)
    result = await db.execute(query)
    rows = result.scalars().all()
    assert len(rows) == 0


# ─── permanent_delete_transactions tests ───

@pytest.mark.asyncio
async def test_permanent_delete_single_with_tags(db, state):
    """永久删除单条交易并清除其标签关联"""
    t = await _add_transaction(
        db, state, amount=8800, tag_ids=[state.tag_ids[0], state.tag_ids[1]], ts=1690001000)
    t.deleted = 1
    t.deleted_at = int(time.time())
    await db.commit()

    count = await permanent_delete_transactions(db, state.uid, [t.id])
    assert count == 1

    # Transaction hard-deleted
    r = await db.execute(select(Transaction).where(Transaction.id == t.id))
    assert r.scalar_one_or_none() is None

    # TransactionTag rows hard-deleted
    r2 = await db.execute(select(TransactionTag).where(TransactionTag.transaction_id == t.id))
    assert len(r2.scalars().all()) == 0


@pytest.mark.asyncio
async def test_permanent_delete_multiple(db, state):
    """批量永久删除多条交易"""
    t1 = await _add_transaction(db, state, amount=1000, ts=1690002000)
    t2 = await _add_transaction(db, state, amount=2000, ts=1690002001)
    t3 = await _add_transaction(db, state, amount=3000, ts=1690002002)
    now_ts = int(time.time())
    t1.deleted = 1
    t1.deleted_at = now_ts
    t2.deleted = 1
    t2.deleted_at = now_ts
    t3.deleted = 1
    t3.deleted_at = now_ts
    await db.commit()

    count = await permanent_delete_transactions(db, state.uid, [t1.id, t2.id, t3.id])
    assert count == 3

    for tid in [t1.id, t2.id, t3.id]:
        r = await db.execute(select(Transaction).where(Transaction.id == tid))
        assert r.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_permanent_delete_nonexistent_ids(db, state):
    """删除不存在的 ID 不报错，返回 0"""
    count = await permanent_delete_transactions(db, state.uid, [999991, 999992])
    assert count == 0


@pytest.mark.asyncio
async def test_permanent_delete_other_user_not_affected(db, state):
    """不影响其他用户的交易"""
    # Create another user
    other = User(username="perm_del_other", email="other@test.com", password=hash_password("123"))
    db.add(other)
    await db.flush()

    # Soft-deleted transaction for the other user
    other_t = Transaction(
        uid=other.id, amount=7700, category_id=state.cat_ids[0],
        transaction_time=1690003000, created_at=1690003000, updated_at=1690003000,
        deleted=1, deleted_at=1690003000,
    )
    db.add(other_t)
    await db.flush()

    # Soft-deleted transaction for state.uid
    own_t = await _add_transaction(db, state, amount=6600, ts=1690003100)
    own_t.deleted = 1
    own_t.deleted_at = int(time.time())
    await db.commit()

    # Attempt to delete both — should only delete own_t
    count = await permanent_delete_transactions(db, state.uid, [own_t.id, other_t.id])
    assert count == 1

    # Other user's transaction still exists
    r = await db.execute(select(Transaction).where(Transaction.id == other_t.id))
    assert r.scalar_one_or_none() is not None
