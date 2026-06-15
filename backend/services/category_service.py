import time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from models.expense_category import ExpenseCategory
from models.expense import Expense
from models.expense_tag_index import ExpenseTagIndex
from middleware.error_handler import NotFoundException, BadRequestException
from schemas.category import CategoryCreate, CategoryUpdate, CategorySortRequest, CategoryResponse
from .catalog_core import find_or_404, soft_delete, sort_models, list_ordered, next_display_order


async def list_categories(db: AsyncSession, uid: int) -> list[CategoryResponse]:
    categories = await list_ordered(db, uid, ExpenseCategory)

    if not categories:
        return []

    cat_ids = [c.id for c in categories]
    stats_result = await db.execute(
        select(
            Expense.category_id,
            func.count(Expense.id).label("cnt"),
            func.coalesce(func.sum(Expense.amount), 0).label("total"),
        )
        .where(
            Expense.uid == uid,
            Expense.category_id.in_(cat_ids),
            Expense.deleted == 0,
        )
        .group_by(Expense.category_id)
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
            expense_count=cnt,
            total_amount=total,
        ))
    return resp


async def create_category(db: AsyncSession, uid: int, req: CategoryCreate) -> ExpenseCategory:
    now = int(time.time())
    order = await next_display_order(db, uid, ExpenseCategory)

    cat = ExpenseCategory(
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


async def update_category(db: AsyncSession, uid: int, category_id: int, req: CategoryUpdate) -> ExpenseCategory:
    cat = await find_or_404(db, uid, ExpenseCategory, category_id, "分类")

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
    await find_or_404(db, uid, ExpenseCategory, category_id, "分类")

    expense_count = await db.execute(
        select(func.count(Expense.id)).where(
            Expense.uid == uid,
            Expense.category_id == category_id,
            Expense.deleted == 0,
        )
    )
    if expense_count.scalar() > 0:
        raise BadRequestException("该分类下已有支出记录，无法删除")

    return await soft_delete(db, uid, ExpenseCategory, category_id, "分类")


async def sort_categories(db: AsyncSession, uid: int, req: CategorySortRequest) -> list[ExpenseCategory]:
    orders = [{"id": item.id, "display_order": item.display_order} for item in req.orders]
    return await sort_models(db, uid, ExpenseCategory, orders)


async def get_categories_by_tag(db: AsyncSession, uid: int, tag_id: int) -> list[CategoryResponse]:
    """查询某标签下历史使用过的分类"""
    result = await db.execute(
        select(
            ExpenseCategory.id,
            ExpenseCategory.name,
            ExpenseCategory.icon,
            ExpenseCategory.color,
            ExpenseCategory.display_order,
        )
        .join(Expense, Expense.category_id == ExpenseCategory.id)
        .join(ExpenseTagIndex, ExpenseTagIndex.expense_id == Expense.id)
        .where(
            Expense.uid == uid,
            ExpenseTagIndex.tag_id == tag_id,
            Expense.deleted == 0,
            ExpenseTagIndex.deleted == 0,
            ExpenseCategory.deleted == 0,
        )
        .distinct()
        .order_by(ExpenseCategory.display_order)
    )
    rows = result.all()
    return [
        CategoryResponse(id=r.id, name=r.name, icon=r.icon, color=r.color, display_order=r.display_order)
        for r in rows
    ]
