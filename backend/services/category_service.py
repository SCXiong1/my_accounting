import time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from models.expense_category import ExpenseCategory
from models.expense import Expense
from middleware.error_handler import NotFoundException, BadRequestException
from schemas.category import CategoryCreate, CategoryUpdate, CategorySortRequest, CategoryResponse


async def list_categories(db: AsyncSession, uid: int) -> list[CategoryResponse]:
    result = await db.execute(
        select(ExpenseCategory)
        .where(ExpenseCategory.uid == uid, ExpenseCategory.deleted == 0)
        .order_by(ExpenseCategory.display_order)
    )
    categories = result.scalars().all()

    resp = []
    for cat in categories:
        count_result = await db.execute(
            select(func.count(Expense.id), func.coalesce(func.sum(Expense.amount), 0))
            .where(
                Expense.uid == uid,
                Expense.category_id == cat.id,
                Expense.deleted == 0,
            )
        )
        cnt, total = count_result.one()
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

    max_order = await db.execute(
        select(func.coalesce(func.max(ExpenseCategory.display_order), -1))
        .where(ExpenseCategory.uid == uid, ExpenseCategory.deleted == 0)
    )
    order = max_order.scalar() + 1

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
    result = await db.execute(
        select(ExpenseCategory).where(
            ExpenseCategory.id == category_id,
            ExpenseCategory.uid == uid,
            ExpenseCategory.deleted == 0,
        )
    )
    cat = result.scalar_one_or_none()
    if not cat:
        raise NotFoundException("分类")

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
    result = await db.execute(
        select(ExpenseCategory).where(
            ExpenseCategory.id == category_id,
            ExpenseCategory.uid == uid,
            ExpenseCategory.deleted == 0,
        )
    )
    cat = result.scalar_one_or_none()
    if not cat:
        raise NotFoundException("分类")

    expense_count = await db.execute(
        select(func.count(Expense.id)).where(
            Expense.uid == uid,
            Expense.category_id == category_id,
            Expense.deleted == 0,
        )
    )
    if expense_count.scalar() > 0:
        raise BadRequestException("该分类下已有支出记录，无法删除")

    now = int(time.time())
    cat.deleted = 1
    cat.deleted_at = now
    cat.updated_at = now
    await db.commit()
    return {"deleted": True}


async def sort_categories(db: AsyncSession, uid: int, req: CategorySortRequest) -> list[ExpenseCategory]:
    now = int(time.time())
    for item in req.orders:
        result = await db.execute(
            select(ExpenseCategory).where(
                ExpenseCategory.id == item.id,
                ExpenseCategory.uid == uid,
                ExpenseCategory.deleted == 0,
            )
        )
        cat = result.scalar_one_or_none()
        if cat:
            cat.display_order = item.display_order
            cat.updated_at = now
    await db.commit()

    return await _list_models(db, uid)


async def _list_models(db: AsyncSession, uid: int) -> list[ExpenseCategory]:
    result = await db.execute(
        select(ExpenseCategory)
        .where(ExpenseCategory.uid == uid, ExpenseCategory.deleted == 0)
        .order_by(ExpenseCategory.display_order)
    )
    return result.scalars().all()
