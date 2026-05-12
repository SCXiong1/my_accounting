import time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from models.expense_tag import ExpenseTag
from models.expense_tag_index import ExpenseTagIndex
from models.expense import Expense
from middleware.error_handler import NotFoundException
from schemas.tag import TagCreate, TagUpdate, TagSortRequest, TagResponse


async def list_tags(db: AsyncSession, uid: int) -> list[TagResponse]:
    result = await db.execute(
        select(ExpenseTag)
        .where(ExpenseTag.uid == uid, ExpenseTag.deleted == 0)
        .order_by(ExpenseTag.display_order)
    )
    tags = result.scalars().all()

    resp = []
    for tag in tags:
        count_result = await db.execute(
            select(func.count(ExpenseTagIndex.id))
            .join(Expense, Expense.id == ExpenseTagIndex.expense_id)
            .where(
                ExpenseTagIndex.tag_id == tag.id,
                ExpenseTagIndex.uid == uid,
                Expense.deleted == 0,
            )
        )
        cnt = count_result.scalar()
        resp.append(TagResponse(
            id=tag.id,
            name=tag.name,
            display_order=tag.display_order,
            expense_count=cnt,
        ))
    return resp


async def create_tag(db: AsyncSession, uid: int, req: TagCreate) -> ExpenseTag:
    now = int(time.time())

    max_order = await db.execute(
        select(func.coalesce(func.max(ExpenseTag.display_order), -1))
        .where(ExpenseTag.uid == uid, ExpenseTag.deleted == 0)
    )
    order = max_order.scalar() + 1

    tag = ExpenseTag(
        uid=uid,
        name=req.name,
        display_order=order,
        created_at=now,
        updated_at=now,
    )
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return tag


async def update_tag(db: AsyncSession, uid: int, tag_id: int, req: TagUpdate) -> ExpenseTag:
    result = await db.execute(
        select(ExpenseTag).where(
            ExpenseTag.id == tag_id,
            ExpenseTag.uid == uid,
            ExpenseTag.deleted == 0,
        )
    )
    tag = result.scalar_one_or_none()
    if not tag:
        raise NotFoundException("标签")

    now = int(time.time())
    if req.name is not None:
        tag.name = req.name
    tag.updated_at = now

    await db.commit()
    await db.refresh(tag)
    return tag


async def delete_tag(db: AsyncSession, uid: int, tag_id: int) -> dict:
    result = await db.execute(
        select(ExpenseTag).where(
            ExpenseTag.id == tag_id,
            ExpenseTag.uid == uid,
            ExpenseTag.deleted == 0,
        )
    )
    tag = result.scalar_one_or_none()
    if not tag:
        raise NotFoundException("标签")

    now = int(time.time())
    tag.deleted = 1
    tag.deleted_at = now
    tag.updated_at = now

    await db.execute(
        delete(ExpenseTagIndex).where(
            ExpenseTagIndex.tag_id == tag_id,
            ExpenseTagIndex.uid == uid,
        )
    )

    await db.commit()
    return {"deleted": True}


async def sort_tags(db: AsyncSession, uid: int, req: TagSortRequest) -> list[ExpenseTag]:
    now = int(time.time())
    for item in req.orders:
        result = await db.execute(
            select(ExpenseTag).where(
                ExpenseTag.id == item.id,
                ExpenseTag.uid == uid,
                ExpenseTag.deleted == 0,
            )
        )
        tag = result.scalar_one_or_none()
        if tag:
            tag.display_order = item.display_order
            tag.updated_at = now
    await db.commit()

    result = await db.execute(
        select(ExpenseTag)
        .where(ExpenseTag.uid == uid, ExpenseTag.deleted == 0)
        .order_by(ExpenseTag.display_order)
    )
    return result.scalars().all()
