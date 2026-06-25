"""Category service unit tests."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from database import Base
from models.category import Category
from models.user import User
from services.category_service import (
    create_category,
    delete_category,
    get_categories_by_tag,
    list_categories,
    update_category,
)
from schemas.category import CategoryCreate, CategoryUpdate

pytest_plugins = ["conftest_unit"]


@pytest_asyncio.fixture
async def db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def user(db: AsyncSession):
    import time
    from utils.security import hash_pin

    user = User(
        username="testuser",
        password=hash_pin("1234"),
        nickname="测试用户",
        pin_changed=1,
        created_at=int(time.time()),
        updated_at=int(time.time()),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.mark.asyncio
async def test_list_categories_empty(db: AsyncSession, user: User):
    result = await list_categories(db, user.id)
    assert result == []


@pytest.mark.asyncio
async def test_create_category(db: AsyncSession, user: User):
    req = CategoryCreate(name="餐饮", icon="🍽️", color="#FF5722")
    cat = await create_category(db, user.id, req)

    assert cat.name == "餐饮"
    assert cat.icon == "🍽️"
    assert cat.color == "#FF5722"
    assert cat.display_order == 0
    assert cat.uid == user.id


@pytest.mark.asyncio
async def test_create_category_auto_display_order(db: AsyncSession, user: User):
    req1 = CategoryCreate(name="餐饮", icon="🍽️", color="#FF5722")
    req2 = CategoryCreate(name="交通", icon="🚗", color="#2196F3")

    cat1 = await create_category(db, user.id, req1)
    cat2 = await create_category(db, user.id, req2)

    assert cat1.display_order == 0
    assert cat2.display_order == 1


@pytest.mark.asyncio
async def test_list_categories_with_stats(db: AsyncSession, user: User):
    req = CategoryCreate(name="餐饮", icon="🍽️", color="#FF5722")
    await create_category(db, user.id, req)

    result = await list_categories(db, user.id)

    assert len(result) == 1
    assert result[0].name == "餐饮"
    assert result[0].transaction_count == 0
    assert result[0].total_amount == 0


@pytest.mark.asyncio
async def test_update_category(db: AsyncSession, user: User):
    req = CategoryCreate(name="餐饮", icon="🍽️", color="#FF5722")
    cat = await create_category(db, user.id, req)

    update_req = CategoryUpdate(name="美食")
    updated = await update_category(db, user.id, cat.id, update_req)

    assert updated.name == "美食"
    assert updated.icon == "🍽️"


@pytest.mark.asyncio
async def test_update_category_not_found(db: AsyncSession, user: User):
    update_req = CategoryUpdate(name="美食")

    with pytest.raises(Exception):
      await update_category(db, user.id, 999, update_req)


@pytest.mark.asyncio
async def test_delete_category(db: AsyncSession, user: User):
    req = CategoryCreate(name="餐饮", icon="🍽️", color="#FF5722")
    cat = await create_category(db, user.id, req)

    result = await delete_category(db, user.id, cat.id)
    assert result["deleted"] is True

    remaining = await list_categories(db, user.id)
    assert len(remaining) == 0


@pytest.mark.asyncio
async def test_get_categories_by_tag_empty(db: AsyncSession, user: User):
    result = await get_categories_by_tag(db, user.id, 1)
    assert result == []
