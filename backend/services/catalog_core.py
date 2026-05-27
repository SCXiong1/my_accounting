"""泛型 CRUD 辅助函数 —— 消除 category/tag service 中的重复模板"""
import time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from middleware.error_handler import NotFoundException


async def find_or_404(db: AsyncSession, uid: int, model, model_id: int, name: str):
    """按 id+uid+deleted=0 查找，未找到抛出 NotFoundException"""
    result = await db.execute(
        select(model).where(
            model.id == model_id,
            model.uid == uid,
            model.deleted == 0,
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise NotFoundException(name)
    return obj


async def soft_delete(db: AsyncSession, uid: int, model, model_id: int, name: str) -> dict:
    """软删除：设置 deleted=1, deleted_at=now"""
    obj = await find_or_404(db, uid, model, model_id, name)
    now = int(time.time())
    obj.deleted = 1
    obj.deleted_at = now
    obj.updated_at = now
    await db.commit()
    return {"deleted": True}


async def list_ordered(db: AsyncSession, uid: int, model) -> list:
    """按 display_order 排列的未删除项列表"""
    result = await db.execute(
        select(model)
        .where(model.uid == uid, model.deleted == 0)
        .order_by(model.display_order)
    )
    return list(result.scalars().all())


async def sort_models(db: AsyncSession, uid: int, model, orders: list[dict]) -> list:
    """批量更新 display_order 后返回重排列表"""
    now = int(time.time())
    ids = [item["id"] for item in orders]
    result = await db.execute(
        select(model).where(
            model.id.in_(ids),
            model.uid == uid,
            model.deleted == 0,
        )
    )
    obj_map = {obj.id: obj for obj in result.scalars().all()}
    for item in orders:
        obj = obj_map.get(item["id"])
        if obj:
            obj.display_order = item["display_order"]
            obj.updated_at = now
    await db.commit()

    return await list_ordered(db, uid, model)


async def next_display_order(db: AsyncSession, uid: int, model) -> int:
    """下一个 display_order 值"""
    result = await db.execute(
        select(func.coalesce(func.max(model.display_order), -1))
        .where(model.uid == uid, model.deleted == 0)
    )
    return result.scalar() + 1
