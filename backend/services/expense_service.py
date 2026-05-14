import time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete, or_
from models.expense import Expense
from models.expense_category import ExpenseCategory
from models.expense_tag import ExpenseTag
from models.expense_tag_index import ExpenseTagIndex
from middleware.error_handler import NotFoundException
from schemas.expense import (
    ExpenseCreate, ExpenseUpdate, ExpenseResponse, ExpenseListResponse,
    CategoryBrief, TagBrief,
)

SORT_FIELDS = {
    "time": Expense.transaction_time,
    "amount": Expense.amount,
}


def _apply_order(query, sort_by: str):
    col = SORT_FIELDS.get(sort_by, Expense.transaction_time)
    return query.order_by(col.desc(), Expense.id.desc())


def _apply_keyword(query, keyword: str | None, uid: int):
    """智能关键词搜索：金额、分类、标签、备注"""
    if not keyword:
        return query

    kw = keyword.strip()
    conditions = [Expense.note.contains(kw)]

    # 金额搜索：精确匹配或前缀匹配（单位：分）
    try:
        amount_val = int(kw)
        conditions.append(Expense.amount == amount_val)
    except ValueError:
        pass

    # 分类名搜索
    cat_sub = select(ExpenseCategory.id).where(
        ExpenseCategory.uid == uid,
        ExpenseCategory.name.contains(kw),
        ExpenseCategory.deleted == 0,
    ).subquery()
    conditions.append(Expense.category_id.in_(cat_sub))

    # 标签名搜索
    tag_sub = select(ExpenseTagIndex.expense_id).join(
        ExpenseTag, ExpenseTag.id == ExpenseTagIndex.tag_id
    ).where(
        ExpenseTag.uid == uid,
        ExpenseTag.name.contains(kw),
        ExpenseTag.deleted == 0,
    ).subquery()
    conditions.append(Expense.id.in_(tag_sub))

    return query.where(or_(*conditions))


async def list_expenses(
    db: AsyncSession,
    uid: int,
    cursor: int | None = None,
    limit: int = 20,
    start_time: int | None = None,
    end_time: int | None = None,
    category_id: int | None = None,
    tag_id: int | None = None,
    keyword: str | None = None,
    sort_by: str = "time",
) -> ExpenseListResponse:
    query = select(Expense).where(Expense.uid == uid, Expense.deleted == 0)
    count_query = select(func.count(Expense.id)).where(Expense.uid == uid, Expense.deleted == 0)

    if cursor:
        query = query.where(Expense.id < cursor)
        count_query = count_query.where(Expense.id < cursor)
    if start_time:
        query = query.where(Expense.transaction_time >= start_time)
        count_query = count_query.where(Expense.transaction_time >= start_time)
    if end_time:
        query = query.where(Expense.transaction_time <= end_time)
        count_query = count_query.where(Expense.transaction_time <= end_time)
    if category_id:
        query = query.where(Expense.category_id == category_id)
        count_query = count_query.where(Expense.category_id == category_id)
    if tag_id:
        tag_subquery = select(ExpenseTagIndex.expense_id).where(
            ExpenseTagIndex.tag_id == tag_id,
            ExpenseTagIndex.uid == uid,
        ).subquery()
        query = query.where(Expense.id.in_(tag_subquery))
        count_query = count_query.where(Expense.id.in_(tag_subquery))

    query = _apply_keyword(query, keyword, uid)
    count_query = _apply_keyword(count_query, keyword, uid)

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = _apply_order(query, sort_by)
    query = query.limit(limit + 1)
    result = await db.execute(query)
    expenses = result.scalars().all()

    has_more = len(expenses) > limit
    if has_more:
        expenses = expenses[:limit]

    items = [_build_response(expense) for expense in expenses]
    await _fill_relations(db, uid, items, expenses)

    return ExpenseListResponse(
        items=items,
        next_cursor=items[-1].id if has_more else None,
        total=total,
    )


async def get_expense(db: AsyncSession, uid: int, expense_id: int) -> ExpenseResponse:
    result = await db.execute(
        select(Expense).where(
            Expense.id == expense_id,
            Expense.uid == uid,
            Expense.deleted == 0,
        )
    )
    expense = result.scalar_one_or_none()
    if not expense:
        raise NotFoundException("支出记录")

    item = _build_response(expense)
    await _fill_relations(db, uid, [item], [expense])
    return item


async def create_expense(db: AsyncSession, uid: int, req: ExpenseCreate) -> ExpenseResponse:
    now = int(time.time())
    category = await db.execute(
        select(ExpenseCategory).where(
            ExpenseCategory.id == req.category_id,
            ExpenseCategory.uid == uid,
            ExpenseCategory.deleted == 0,
        )
    )
    if not category.scalar_one_or_none():
        raise NotFoundException("分类")

    expense = Expense(
        uid=uid,
        amount=req.amount,
        category_id=req.category_id,
        transaction_time=req.transaction_time,
        timezone_offset=req.timezone_offset,
        note=req.note,
        created_at=now,
        updated_at=now,
    )
    db.add(expense)
    await db.flush()

    for tag_id in req.tag_ids:
        db.add(ExpenseTagIndex(
            uid=uid,
            expense_id=expense.id,
            tag_id=tag_id,
            created_at=now,
        ))

    await db.commit()
    await db.refresh(expense)

    return await get_expense(db, uid, expense.id)


async def update_expense(db: AsyncSession, uid: int, expense_id: int, req: ExpenseUpdate) -> ExpenseResponse:
    result = await db.execute(
        select(Expense).where(
            Expense.id == expense_id,
            Expense.uid == uid,
            Expense.deleted == 0,
        )
    )
    expense = result.scalar_one_or_none()
    if not expense:
        raise NotFoundException("支出记录")

    now = int(time.time())
    if req.amount is not None:
        expense.amount = req.amount
    if req.category_id is not None:
        category = await db.execute(
            select(ExpenseCategory).where(
                ExpenseCategory.id == req.category_id,
                ExpenseCategory.uid == uid,
                ExpenseCategory.deleted == 0,
            )
        )
        if not category.scalar_one_or_none():
            raise NotFoundException("分类")
        expense.category_id = req.category_id
    if req.transaction_time is not None:
        expense.transaction_time = req.transaction_time
    if req.timezone_offset is not None:
        expense.timezone_offset = req.timezone_offset
    if req.note is not None:
        expense.note = req.note

    if req.tag_ids is not None:
        await db.execute(
            delete(ExpenseTagIndex).where(ExpenseTagIndex.expense_id == expense_id)
        )
        for tag_id in req.tag_ids:
            db.add(ExpenseTagIndex(
                uid=uid,
                expense_id=expense_id,
                tag_id=tag_id,
                created_at=now,
            ))

    expense.updated_at = now
    await db.commit()
    await db.refresh(expense)

    return await get_expense(db, uid, expense.id)


async def delete_expense(db: AsyncSession, uid: int, expense_id: int) -> dict:
    result = await db.execute(
        select(Expense).where(
            Expense.id == expense_id,
            Expense.uid == uid,
            Expense.deleted == 0,
        )
    )
    expense = result.scalar_one_or_none()
    if not expense:
        raise NotFoundException("支出记录")

    now = int(time.time())
    expense.deleted = 1
    expense.deleted_at = now
    expense.updated_at = now

    await db.execute(
        delete(ExpenseTagIndex).where(ExpenseTagIndex.expense_id == expense_id)
    )

    await db.commit()
    return {"deleted": True}


def _build_response(expense: Expense) -> ExpenseResponse:
    return ExpenseResponse(
        id=expense.id,
        amount=expense.amount,
        category=CategoryBrief(id=0, name="", icon="", color=""),
        tags=[],
        transaction_time=expense.transaction_time,
        timezone_offset=expense.timezone_offset,
        note=expense.note,
    )


async def _fill_relations(db: AsyncSession, uid: int, items: list[ExpenseResponse], expenses: list[Expense]):
    cat_ids = list(set(e.category_id for e in expenses))
    if cat_ids:
        cat_result = await db.execute(
            select(ExpenseCategory).where(
                ExpenseCategory.id.in_(cat_ids),
                ExpenseCategory.deleted == 0,
            )
        )
        cat_map = {c.id: c for c in cat_result.scalars().all()}
        for item, expense in zip(items, expenses):
            cat = cat_map.get(expense.category_id)
            if cat:
                item.category = CategoryBrief(id=cat.id, name=cat.name, icon=cat.icon, color=cat.color)

    expense_ids = [e.id for e in expenses]
    if expense_ids:
        eti_result = await db.execute(
            select(ExpenseTagIndex, ExpenseTag).join(
                ExpenseTag, ExpenseTag.id == ExpenseTagIndex.tag_id
            ).where(
                ExpenseTagIndex.expense_id.in_(expense_ids),
                ExpenseTagIndex.uid == uid,
                ExpenseTag.deleted == 0,
            )
        )
        tag_map: dict[int, list[TagBrief]] = {}
        for eti, tag in eti_result.all():
            tag_map.setdefault(eti.expense_id, []).append(TagBrief(id=tag.id, name=tag.name))
        for item in items:
            item.tags = tag_map.get(item.id, [])
