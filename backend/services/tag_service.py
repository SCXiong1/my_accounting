import time

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from middleware.error_handler import BadRequestException
from models.tag import Tag
from models.transaction import Transaction
from models.transaction_tag import TransactionTag
from schemas.tag import TagCreate, TagResponse, TagSortRequest, TagUpdate

from .catalog_core import delete_entity, find_or_404, list_ordered, next_display_order, sort_models


async def list_tags(db: AsyncSession, uid: int) -> list[TagResponse]:
    tags = await list_ordered(db, uid, Tag)

    if not tags:
        return []

    tag_ids = [t.id for t in tags]
    stats_result = await db.execute(
        select(
            TransactionTag.tag_id,
            func.count(TransactionTag.id).label("cnt"),
        )
        .join(Transaction, Transaction.id == TransactionTag.transaction_id)
        .where(
            TransactionTag.tag_id.in_(tag_ids),
            TransactionTag.uid == uid,
            Transaction.deleted == 0,
        )
        .group_by(TransactionTag.tag_id)
    )
    stats = {row.tag_id: row.cnt for row in stats_result.all()}

    resp = []
    for tag in tags:
        cnt = stats.get(tag.id, 0)
        resp.append(TagResponse(
            id=tag.id,
            name=tag.name,
            display_order=tag.display_order,
            transaction_count=cnt,
        ))
    return resp


async def create_tag(db: AsyncSession, uid: int, req: TagCreate) -> Tag:
    existing = await db.execute(
        select(Tag).where(
            Tag.uid == uid,
            Tag.name == req.name.strip(),
        )
    )
    if existing.scalar_one_or_none():
        raise BadRequestException(f"标签「{req.name.strip()}」已存在，请勿重复创建")

    now = int(time.time())
    order = await next_display_order(db, uid, Tag)

    tag = Tag(
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


async def update_tag(db: AsyncSession, uid: int, tag_id: int, req: TagUpdate) -> Tag:
    tag = await find_or_404(db, uid, Tag, tag_id, "标签")

    now = int(time.time())
    if req.name is not None:
        tag.name = req.name
    tag.updated_at = now

    await db.commit()
    await db.refresh(tag)
    return tag


async def delete_tag(db: AsyncSession, uid: int, tag_id: int) -> dict:
    await find_or_404(db, uid, Tag, tag_id, "标签")

    tag_index_count = await db.execute(
        select(func.count(TransactionTag.id)).where(
            TransactionTag.uid == uid,
            TransactionTag.tag_id == tag_id,
        )
    )
    if tag_index_count.scalar() > 0:
        raise BadRequestException("该标签下已有支出记录，无法删除")

    return await delete_entity(db, uid, Tag, tag_id, "标签")


async def sort_tags(db: AsyncSession, uid: int, req: TagSortRequest) -> list[Tag]:
    orders = [{"id": item.id, "display_order": item.display_order} for item in req.orders]
    return await sort_models(db, uid, Tag, orders)


async def get_tags_by_category(db: AsyncSession, uid: int, category_id: int) -> list[TagResponse]:
    """查询某分类下历史使用过的标签"""
    result = await db.execute(
        select(Tag.id, Tag.name, Tag.display_order)
        .join(TransactionTag, TransactionTag.tag_id == Tag.id)
        .join(Transaction, Transaction.id == TransactionTag.transaction_id)
        .where(
            Transaction.uid == uid,
            Transaction.category_id == category_id,
            Transaction.deleted == 0,
        )
        .distinct()
        .order_by(Tag.display_order)
    )
    rows = result.all()
    return [TagResponse(id=r.id, name=r.name, display_order=r.display_order) for r in rows]
