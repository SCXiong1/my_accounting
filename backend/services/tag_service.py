import time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from models.expense_tag import ExpenseTag
from models.expense_tag_index import ExpenseTagIndex
from models.expense import Expense
from middleware.error_handler import BadRequestException
from schemas.tag import TagCreate, TagUpdate, TagSortRequest, TagResponse
from .catalog_core import find_or_404, soft_delete, sort_models, list_ordered, next_display_order


async def list_tags(db: AsyncSession, uid: int) -> list[TagResponse]:
    tags = await list_ordered(db, uid, ExpenseTag)

    if not tags:
        return []

    tag_ids = [t.id for t in tags]
    stats_result = await db.execute(
        select(
            ExpenseTagIndex.tag_id,
            func.count(ExpenseTagIndex.id).label("cnt"),
        )
        .join(Expense, Expense.id == ExpenseTagIndex.expense_id)
        .where(
            ExpenseTagIndex.tag_id.in_(tag_ids),
            ExpenseTagIndex.uid == uid,
            ExpenseTagIndex.deleted == 0,
            Expense.deleted == 0,
        )
        .group_by(ExpenseTagIndex.tag_id)
    )
    stats = {row.tag_id: row.cnt for row in stats_result.all()}

    resp = []
    for tag in tags:
        cnt = stats.get(tag.id, 0)
        resp.append(TagResponse(
            id=tag.id,
            name=tag.name,
            display_order=tag.display_order,
            expense_count=cnt,
        ))
    return resp


async def create_tag(db: AsyncSession, uid: int, req: TagCreate) -> ExpenseTag:
    existing = await db.execute(
        select(ExpenseTag).where(
            ExpenseTag.uid == uid,
            ExpenseTag.name == req.name.strip(),
            ExpenseTag.deleted == 0,
        )
    )
    if existing.scalar_one_or_none():
        raise BadRequestException(f"标签「{req.name.strip()}」已存在，请勿重复创建")

    now = int(time.time())
    order = await next_display_order(db, uid, ExpenseTag)

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
    tag = await find_or_404(db, uid, ExpenseTag, tag_id, "标签")

    now = int(time.time())
    if req.name is not None:
        tag.name = req.name
    tag.updated_at = now

    await db.commit()
    await db.refresh(tag)
    return tag


async def delete_tag(db: AsyncSession, uid: int, tag_id: int) -> dict:
    return await soft_delete(db, uid, ExpenseTag, tag_id, "标签")


async def sort_tags(db: AsyncSession, uid: int, req: TagSortRequest) -> list[ExpenseTag]:
    orders = [{"id": item.id, "display_order": item.display_order} for item in req.orders]
    return await sort_models(db, uid, ExpenseTag, orders)
