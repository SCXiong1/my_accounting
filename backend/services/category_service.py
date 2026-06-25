import time

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from middleware.error_handler import BadRequestException
from models.category import Category
from models.transaction import Transaction
from models.transaction_tag import TransactionTag
from schemas.category import CategoryCreate, CategoryResponse, CategorySortRequest, CategoryUpdate

from .catalog_core import delete_entity, find_or_404, list_ordered, next_display_order, sort_models


async def list_categories(db: AsyncSession, uid: int) -> list[CategoryResponse]:
    categories = await list_ordered(db, uid, Category)

    if not categories:
        return []

    cat_ids = [c.id for c in categories]
    stats_result = await db.execute(
        select(
            Transaction.category_id,
            func.count(Transaction.id).label("cnt"),
            func.coalesce(func.sum(Transaction.amount), 0).label("total"),
        )
        .where(
            Transaction.uid == uid,
            Transaction.category_id.in_(cat_ids),
            Transaction.deleted == 0,
        )
        .group_by(Transaction.category_id)
    )
    stats = {row.category_id: (row.cnt, row.total) for row in stats_result.all()}

    resp = []
    for cat in categories:
        cnt, total = stats.get(cat.id, (0, 0))
        resp.append(CategoryResponse(
            id=cat.id,
            name=cat.name,
            icon=cat.icon,
            color=cat.color,
            display_order=cat.display_order,
            transaction_count=cnt,
            total_amount=total,
        ))
    return resp


async def create_category(db: AsyncSession, uid: int, req: CategoryCreate) -> Category:
    now = int(time.time())
    order = await next_display_order(db, uid, Category)

    cat = Category(
        uid=uid,
        name=req.name,
        icon=req.icon,
        color=req.color,
        display_order=order,
        created_at=now,
        updated_at=now,
    )
    db.add(cat)
    await db.commit()
    await db.refresh(cat)
    return cat


async def update_category(db: AsyncSession, uid: int, category_id: int, req: CategoryUpdate) -> Category:
    cat = await find_or_404(db, uid, Category, category_id, "分类")

    now = int(time.time())
    if req.name is not None:
        cat.name = req.name
    if req.icon is not None:
        cat.icon = req.icon
    if req.color is not None:
        cat.color = req.color
    cat.updated_at = now

    await db.commit()
    await db.refresh(cat)
    return cat


async def delete_category(db: AsyncSession, uid: int, category_id: int) -> dict:
    await find_or_404(db, uid, Category, category_id, "分类")

    transaction_count = await db.execute(
        select(func.count(Transaction.id)).where(
            Transaction.uid == uid,
            Transaction.category_id == category_id,
            Transaction.deleted == 0,
        )
    )
    if transaction_count.scalar() > 0:
        raise BadRequestException("该分类下已有支出记录，无法删除")

    return await delete_entity(db, uid, Category, category_id, "分类")


async def sort_categories(db: AsyncSession, uid: int, req: CategorySortRequest) -> list[Category]:
    orders = [{"id": item.id, "display_order": item.display_order} for item in req.orders]
    return await sort_models(db, uid, Category, orders)


async def get_categories_by_tag(db: AsyncSession, uid: int, tag_id: int) -> list[CategoryResponse]:
    """查询某标签下历史使用过的分类"""
    result = await db.execute(
        select(
            Category.id,
            Category.name,
            Category.icon,
            Category.color,
            Category.display_order,
        )
        .join(Transaction, Transaction.category_id == Category.id)
        .join(TransactionTag, TransactionTag.transaction_id == Transaction.id)
        .where(
            Transaction.uid == uid,
            TransactionTag.tag_id == tag_id,
            Transaction.deleted == 0,
        )
        .distinct()
        .order_by(Category.display_order)
    )
    rows = result.all()
    return [
        CategoryResponse(id=r.id, name=r.name, icon=r.icon, color=r.color, display_order=r.display_order)
        for r in rows
    ]
