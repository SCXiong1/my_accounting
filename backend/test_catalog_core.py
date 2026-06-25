"""catalog_core 泛型 CRUD 辅助函数测试"""
import time

import pytest

from middleware.error_handler import NotFoundException
from models.category import Category

pytest_plugins = ["conftest_unit"]


@pytest.mark.asyncio
async def test_find_or_404_found(db, state):
    """找到时返回 model 实例"""
    from services.catalog_core import find_or_404

    cat = await find_or_404(db, state.uid, Category, state.cat_ids[0], "分类")
    assert cat is not None
    assert cat.id == state.cat_ids[0]
    assert cat.name == "餐饮"


@pytest.mark.asyncio
async def test_find_or_404_raises(db, state):
    """未找到时抛出 NotFoundException"""
    from services.catalog_core import find_or_404

    with pytest.raises(NotFoundException):
        await find_or_404(db, state.uid, Category, 99999, "分类")


@pytest.mark.asyncio
async def test_delete_entity(db, state):
    """delete_entity 执行硬删除并返回 dict"""
    from services.catalog_core import delete_entity

    result = await delete_entity(db, state.uid, Category, state.cat_ids[0], "分类")
    assert result == {"deleted": True}

    # 验证行已被物理删除
    from sqlalchemy import select

    r = await db.execute(select(Category).where(Category.id == state.cat_ids[0]))
    assert r.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_sort_models(db, state):
    """sort_models 批量更新 display_order 并返回排序列表"""
    from services.catalog_core import sort_models

    now = int(time.time())
    c1 = Category(uid=state.uid, name="sort1", display_order=5, created_at=now, updated_at=now)
    c2 = Category(uid=state.uid, name="sort2", display_order=2, created_at=now, updated_at=now)
    db.add(c1)
    db.add(c2)
    await db.flush()

    orders = [
        {"id": c2.id, "display_order": 50},
        {"id": c1.id, "display_order": 10},
    ]
    result = await sort_models(db, state.uid, Category, orders)

    assert len(result) >= 2
    ids = [c.id for c in result]
    # c1(display_order=10) 应在 c2(50) 前面
    assert ids.index(c1.id) < ids.index(c2.id), "display_order=10 应在 50 前面"
