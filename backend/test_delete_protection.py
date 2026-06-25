"""Tests for hard delete + delete protection per ADR-0002.

Category, Tag, TransactionTag use hard delete.
Delete protection: can't delete Category/Tag with associated transactions.
"""
import pytest
from sqlalchemy import select

from middleware.error_handler import BadRequestException, NotFoundException
from models.category import Category
from models.tag import Tag
from models.transaction import Transaction
from models.transaction_tag import TransactionTag

pytest_plugins = ["conftest_unit"]


# ---------------------------------------------------------------------------
# Category hard delete
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_delete_category_no_transactions_success(db, state):
    """Delete category with no associated transactions → success, row gone."""
    from services.category_service import delete_category

    # cat_ids[2] = "空分类" has no transactions
    result = await delete_category(db, state.uid, state.cat_ids[2])
    assert result == {"deleted": True}

    # Row should be physically gone
    r = await db.execute(
        select(Category).where(Category.id == state.cat_ids[2])
    )
    assert r.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_delete_category_with_transactions_blocked(db, state):
    """Delete category with associated transactions → 400 error."""
    from services.category_service import delete_category

    # Create a transaction under cat_ids[0] = "餐饮"
    now = 1700000000
    expense = Transaction(
        uid=state.uid,
        amount=1000,
        category_id=state.cat_ids[0],
        transaction_time=now,
        created_at=now,
        updated_at=now,
    )
    db.add(expense)
    await db.flush()

    with pytest.raises(BadRequestException) as exc_info:
        await delete_category(db, state.uid, state.cat_ids[0])
    assert "已有支出记录" in str(exc_info.value.detail)


# ---------------------------------------------------------------------------
# Tag hard delete
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_delete_tag_no_transactions_success(db, state):
    """Delete tag with no associated transactions → success, row gone."""
    from services.tag_service import delete_tag

    # tag_ids[1] = "空标签" has no tag index entries
    result = await delete_tag(db, state.uid, state.tag_ids[1])
    assert result == {"deleted": True}

    # Row should be physically gone
    r = await db.execute(select(Tag).where(Tag.id == state.tag_ids[1]))
    assert r.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_delete_tag_with_transactions_blocked(db, state):
    """Delete tag with associated transactions → 400 error."""
    from services.tag_service import delete_tag

    now = 1700000000
    expense = Transaction(
        uid=state.uid,
        amount=2000,
        category_id=state.cat_ids[0],
        transaction_time=now,
        created_at=now,
        updated_at=now,
    )
    db.add(expense)
    await db.flush()

    db.add(
        TransactionTag(
            uid=state.uid,
            transaction_id=expense.id,
            tag_id=state.tag_ids[0],
            created_at=now,
        )
    )
    await db.flush()

    with pytest.raises(BadRequestException) as exc_info:
        await delete_tag(db, state.uid, state.tag_ids[0])
    assert "已有支出记录" in str(exc_info.value.detail)


# ---------------------------------------------------------------------------
# Category/Tag models no longer have deleted/deleted_at columns
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_category_model_no_soft_delete_columns(db, state):
    """Category model should not have deleted or deleted_at columns."""
    cat = await db.get(Category, state.cat_ids[0])
    assert cat is not None
    assert not hasattr(cat, "deleted"), "Category should not have 'deleted' attribute"
    assert not hasattr(
        cat, "deleted_at"
    ), "Category should not have 'deleted_at' attribute"


@pytest.mark.asyncio
async def test_tag_model_no_soft_delete_columns(db, state):
    """Tag model should not have deleted or deleted_at columns."""
    tag = await db.get(Tag, state.tag_ids[0])
    assert tag is not None
    assert not hasattr(tag, "deleted"), "Tag should not have 'deleted' attribute"
    assert not hasattr(
        tag, "deleted_at"
    ), "Tag should not have 'deleted_at' attribute"


@pytest.mark.asyncio
async def test_tag_index_model_no_soft_delete_columns(db, state):
    """TransactionTag (tag index) model should not have deleted or deleted_at columns."""
    # Create an expense + tag index to test
    now = 1700000000
    expense = Transaction(
        uid=state.uid,
        amount=3000,
        category_id=state.cat_ids[1],
        transaction_time=now,
        created_at=now,
        updated_at=now,
    )
    db.add(expense)
    await db.flush()

    eti = TransactionTag(
        uid=state.uid,
        transaction_id=expense.id,
        tag_id=state.tag_ids[0],
        created_at=now,
    )
    db.add(eti)
    await db.flush()

    row = await db.get(TransactionTag, eti.id)
    assert row is not None
    assert not hasattr(
        row, "deleted"
    ), "TransactionTag should not have 'deleted' attribute"
    assert not hasattr(
        row, "deleted_at"
    ), "TransactionTag should not have 'deleted_at' attribute"


# ---------------------------------------------------------------------------
# Transaction still uses soft delete (unchanged)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_expense_still_uses_soft_delete(db, state):
    """Transaction/Expense model retains soft delete."""
    from services.transaction_service import delete_transaction, get_transaction, restore_transaction

    now = 1700000000
    expense = Transaction(
        uid=state.uid,
        amount=5000,
        category_id=state.cat_ids[1],
        transaction_time=now,
        created_at=now,
        updated_at=now,
    )
    db.add(expense)
    await db.flush()

    # Soft delete
    result = await delete_transaction(db, state.uid, expense.id)
    assert result == {"deleted": True}

    # Should not be accessible via get_transaction (deleted=0 filter)
    with pytest.raises(NotFoundException):
        await get_transaction(db, state.uid, expense.id)

    # Restore
    result = await restore_transaction(db, state.uid, expense.id)
    assert result == {"deleted": False}

    # Should be accessible again
    restored = await get_transaction(db, state.uid, expense.id)
    assert restored.id == expense.id
