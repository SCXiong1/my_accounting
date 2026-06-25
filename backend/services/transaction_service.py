import time

from sqlalchemy import delete as sql_delete
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from constants import DEFAULT_PAGE_SIZE
from middleware.error_handler import NotFoundException
from models.category import Category
from models.tag import Tag
from models.transaction import Transaction
from models.transaction_tag import TransactionTag
from schemas.transaction import (
    CategoryBrief,
    TagBrief,
    TransactionCreate,
    TransactionListResponse,
    TransactionResponse,
    TransactionUpdate,
)

SORT_FIELDS = {
    "time": Transaction.transaction_time,
    "amount": Transaction.amount,
}


async def _validate_tags(db: AsyncSession, uid: int, tag_ids: list[int]) -> None:
    if not tag_ids:
        return
    result = await db.execute(
        select(Tag).where(
            Tag.id.in_(tag_ids),
            Tag.uid == uid,
        )
    )
    valid_ids = {t.id for t in result.scalars().all()}
    invalid = set(tag_ids) - valid_ids
    if invalid:
        raise NotFoundException(f"标签({','.join(map(str, invalid))})")


def _apply_order(query: Select, sort_by: str) -> Select:
    col = SORT_FIELDS.get(sort_by, Transaction.transaction_time)
    return query.order_by(col.desc(), Transaction.id.desc())


def _apply_keyword(query: Select, keyword: str | None, uid: int) -> Select:
    """智能关键词搜索：金额、分类、标签、备注"""
    if not keyword:
        return query

    kw = keyword.strip()
    conditions = [Transaction.note.contains(kw)]

    try:
        amount_val = int(kw)
        conditions.append(Transaction.amount == amount_val)
    except ValueError:
        pass

    cat_sub = select(Category.id).where(
        Category.uid == uid,
        Category.name.contains(kw),
    ).scalar_subquery()
    conditions.append(Transaction.category_id.in_(cat_sub))

    tag_sub = select(TransactionTag.transaction_id).join(
        Tag, Tag.id == TransactionTag.tag_id
    ).where(
        Tag.uid == uid,
        Tag.name.contains(kw),
    ).scalar_subquery()
    conditions.append(Transaction.id.in_(tag_sub))

    return query.where(or_(*conditions))


async def list_transactions(
    db: AsyncSession,
    uid: int,
    cursor: int | None = None,
    limit: int = DEFAULT_PAGE_SIZE,
    start_time: int | None = None,
    end_time: int | None = None,
    category_id: int | None = None,
    tag_id: int | None = None,
    keyword: str | None = None,
    sort_by: str = "time",
    show_deleted: bool = False,
) -> TransactionListResponse:
    deleted_val = 1 if show_deleted else 0
    query = select(Transaction).where(Transaction.uid == uid, Transaction.deleted == deleted_val)
    count_query = select(func.count(Transaction.id)).where(Transaction.uid == uid, Transaction.deleted == deleted_val)

    if cursor:
        query = query.where(Transaction.id < cursor)
        count_query = count_query.where(Transaction.id < cursor)
    if start_time:
        query = query.where(Transaction.transaction_time >= start_time)
        count_query = count_query.where(Transaction.transaction_time >= start_time)
    if end_time:
        query = query.where(Transaction.transaction_time <= end_time)
        count_query = count_query.where(Transaction.transaction_time <= end_time)
    if category_id:
        query = query.where(Transaction.category_id == category_id)
        count_query = count_query.where(Transaction.category_id == category_id)
    if tag_id:
        tag_subquery = select(TransactionTag.transaction_id).where(
            TransactionTag.tag_id == tag_id,
            TransactionTag.uid == uid,
        ).scalar_subquery()
        query = query.where(Transaction.id.in_(tag_subquery))
        count_query = count_query.where(Transaction.id.in_(tag_subquery))

    query = _apply_keyword(query, keyword, uid)
    count_query = _apply_keyword(count_query, keyword, uid)

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = _apply_order(query, sort_by)
    query = query.limit(limit + 1)
    result = await db.execute(query)
    transactions = result.scalars().all()

    has_more = len(transactions) > limit
    if has_more:
        transactions = transactions[:limit]

    items = [_build_response(t) for t in transactions]
    await _fill_relations(db, uid, items, transactions)

    return TransactionListResponse(
        items=items,
        next_cursor=items[-1].id if has_more else None,
        total=total,
    )


async def get_transaction(db: AsyncSession, uid: int, transaction_id: int) -> TransactionResponse:
    result = await db.execute(
        select(Transaction).where(
            Transaction.id == transaction_id,
            Transaction.uid == uid,
            Transaction.deleted == 0,
        )
    )
    transaction = result.scalar_one_or_none()
    if not transaction:
        raise NotFoundException("支出记录")

    item = _build_response(transaction)
    await _fill_relations(db, uid, [item], [transaction])
    return item


async def create_transaction(db: AsyncSession, uid: int, req: TransactionCreate) -> TransactionResponse:
    now = int(time.time())
    category = await db.execute(
        select(Category).where(
            Category.id == req.category_id,
            Category.uid == uid,
        )
    )
    if not category.scalar_one_or_none():
        raise NotFoundException("分类")

    await _validate_tags(db, uid, req.tag_ids)

    transaction = Transaction(
        uid=uid,
        amount=req.amount,
        category_id=req.category_id,
        transaction_time=req.transaction_time,
        timezone_offset=req.timezone_offset,
        note=req.note,
        type=req.type,
        created_at=now,
        updated_at=now,
    )
    db.add(transaction)
    await db.flush()

    for tag_id in req.tag_ids:
        db.add(TransactionTag(
            uid=uid,
            transaction_id=transaction.id,
            tag_id=tag_id,
            created_at=now,
        ))

    await db.commit()

    return await get_transaction(db, uid, transaction.id)


async def update_transaction(
    db: AsyncSession, uid: int, transaction_id: int, req: TransactionUpdate,
) -> TransactionResponse:
    result = await db.execute(
        select(Transaction).where(
            Transaction.id == transaction_id,
            Transaction.uid == uid,
            Transaction.deleted == 0,
        )
    )
    transaction = result.scalar_one_or_none()
    if not transaction:
        raise NotFoundException("支出记录")

    now = int(time.time())
    if req.amount is not None:
        transaction.amount = req.amount
    if req.category_id is not None:
        category = await db.execute(
            select(Category).where(
                Category.id == req.category_id,
                Category.uid == uid,
            )
        )
        if not category.scalar_one_or_none():
            raise NotFoundException("分类")
        transaction.category_id = req.category_id
    if req.transaction_time is not None:
        transaction.transaction_time = req.transaction_time
    if req.timezone_offset is not None:
        transaction.timezone_offset = req.timezone_offset
    if req.note is not None:
        transaction.note = req.note
    if req.type is not None:
        transaction.type = req.type

    if req.tag_ids is not None:
        req.tag_ids = list(set(req.tag_ids))
        await _validate_tags(db, uid, req.tag_ids)

        await db.execute(
            sql_delete(TransactionTag).where(
                TransactionTag.transaction_id == transaction_id,
            )
        )
        for tag_id in req.tag_ids:
            db.add(TransactionTag(
                uid=uid,
                transaction_id=transaction_id,
                tag_id=tag_id,
                created_at=now,
            ))

    transaction.updated_at = now
    await db.commit()

    return await get_transaction(db, uid, transaction.id)


async def restore_transaction(db: AsyncSession, uid: int, transaction_id: int) -> dict:
    result = await db.execute(
        select(Transaction).where(
            Transaction.id == transaction_id,
            Transaction.uid == uid,
            Transaction.deleted == 1,
        )
    )
    transaction = result.scalar_one_or_none()
    if not transaction:
        raise NotFoundException("支出记录")

    now = int(time.time())
    transaction.deleted = 0
    transaction.deleted_at = 0
    transaction.updated_at = now

    await db.commit()
    return {"deleted": False}


async def delete_transaction(db: AsyncSession, uid: int, transaction_id: int) -> dict:
    result = await db.execute(
        select(Transaction).where(
            Transaction.id == transaction_id,
            Transaction.uid == uid,
            Transaction.deleted == 0,
        )
    )
    transaction = result.scalar_one_or_none()
    if not transaction:
        raise NotFoundException("支出记录")

    now = int(time.time())
    transaction.deleted = 1
    transaction.deleted_at = now
    transaction.updated_at = now

    await db.commit()
    return {"deleted": True}


async def permanent_delete_transactions(db: AsyncSession, uid: int, transaction_ids: list[int]) -> int:
    """批量永久删除支出记录（已软删除的），返回实际删除数量"""
    result = await db.execute(
        select(Transaction.id).where(
            Transaction.id.in_(transaction_ids),
            Transaction.uid == uid,
            Transaction.deleted == 1,
        )
    )
    valid_ids = [row[0] for row in result.all()]
    if not valid_ids:
        return 0

    await db.execute(
        sql_delete(TransactionTag).where(
            TransactionTag.transaction_id.in_(valid_ids),
            TransactionTag.uid == uid,
        )
    )

    await db.execute(
        sql_delete(Transaction).where(
            Transaction.id.in_(valid_ids),
            Transaction.uid == uid,
        )
    )

    await db.commit()
    return len(valid_ids)


def _build_response(transaction: Transaction) -> TransactionResponse:
    return TransactionResponse(
        id=transaction.id,
        amount=transaction.amount,
        category=CategoryBrief(id=0, name="", icon="", color=""),
        tags=[],
        transaction_time=transaction.transaction_time,
        timezone_offset=transaction.timezone_offset,
        note=transaction.note,
        type=transaction.type,
    )


async def _fill_relations(
    db: AsyncSession, uid: int, items: list[TransactionResponse], transactions: list[Transaction],
) -> None:
    cat_ids = list(set(t.category_id for t in transactions))
    if cat_ids:
        cat_result = await db.execute(
            select(Category).where(
                Category.id.in_(cat_ids),
            )
        )
        cat_map = {c.id: c for c in cat_result.scalars().all()}
        for item, transaction in zip(items, transactions):
            cat = cat_map.get(transaction.category_id)
            if cat:
                item.category = CategoryBrief(id=cat.id, name=cat.name, icon=cat.icon, color=cat.color)

    transaction_ids = [t.id for t in transactions]
    if transaction_ids:
        tt_result = await db.execute(
            select(TransactionTag, Tag).join(
                Tag, Tag.id == TransactionTag.tag_id
            ).where(
                TransactionTag.transaction_id.in_(transaction_ids),
                TransactionTag.uid == uid,
            )
        )
        tag_map: dict[int, list[TagBrief]] = {}
        for tt, tag in tt_result.all():
            tag_map.setdefault(tt.transaction_id, []).append(TagBrief(id=tag.id, name=tag.name))
        for item in items:
            item.tags = tag_map.get(item.id, [])
