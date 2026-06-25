"""Transaction soft delete + tag index hard-delete behavior tests."""
import pytest
from sqlalchemy import select

from models.transaction_tag import TransactionTag
from schemas.transaction import TransactionCreate, TransactionUpdate
from services.transaction_service import (
    create_transaction,
    delete_transaction,
    get_transaction,
    restore_transaction,
    update_transaction,
)

pytest_plugins = ["conftest_unit"]


@pytest.mark.asyncio
async def test_update_replaces_tag_associations(db, state):
    """Updating tags deletes old associations and creates new ones."""
    req = TransactionCreate(
        amount=5000, category_id=state.cat_ids[0], tag_ids=state.tag_ids[:2], transaction_time=1700000000)
    transaction = await create_transaction(db, state.uid, req)

    update_req = TransactionUpdate(tag_ids=[state.tag_ids[2]])
    await update_transaction(db, state.uid, transaction.id, update_req)

    result = await db.execute(
        select(TransactionTag).where(TransactionTag.transaction_id == transaction.id))
    rows = result.scalars().all()

    assert len(rows) == 1
    assert rows[0].tag_id == state.tag_ids[2]


@pytest.mark.asyncio
async def test_delete_keeps_tag_index_rows_for_restore(db, state):
    """Deleting transaction keeps tag index rows intact (needed for restore)."""
    req = TransactionCreate(
        amount=5000, category_id=state.cat_ids[0], tag_ids=state.tag_ids[:1], transaction_time=1700000000)
    transaction = await create_transaction(db, state.uid, req)

    await delete_transaction(db, state.uid, transaction.id)

    result = await db.execute(
        select(TransactionTag).where(TransactionTag.transaction_id == transaction.id))
    rows = result.scalars().all()
    assert len(rows) == 1
    assert rows[0].tag_id == state.tag_ids[0]


@pytest.mark.asyncio
async def test_restore_preserves_tag_associations(db, state):
    """Restoring transaction still has its tag associations."""
    req = TransactionCreate(
        amount=5000, category_id=state.cat_ids[0], tag_ids=state.tag_ids[:1], transaction_time=1700000000)
    transaction = await create_transaction(db, state.uid, req)

    await delete_transaction(db, state.uid, transaction.id)
    await restore_transaction(db, state.uid, transaction.id)

    restored = await get_transaction(db, state.uid, transaction.id)
    assert len(restored.tags) == 1
    assert restored.tags[0].id == state.tag_ids[0]
