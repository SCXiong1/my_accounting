"""Tag service unit tests."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from database import Base
from models.tag import Tag
from models.user import User
from services.tag_service import (
    create_tag,
    delete_tag,
    get_tags_by_category,
    list_tags,
    update_tag,
)
from schemas.tag import TagCreate, TagUpdate

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
async def test_list_tags_empty(db: AsyncSession, user: User):
    result = await list_tags(db, user.id)
    assert result == []


@pytest.mark.asyncio
async def test_create_tag(db: AsyncSession, user: User):
    req = TagCreate(name="早餐")
    tag = await create_tag(db, user.id, req)

    assert tag.name == "早餐"
    assert tag.display_order == 0
    assert tag.uid == user.id


@pytest.mark.asyncio
async def test_create_tag_auto_display_order(db: AsyncSession, user: User):
    req1 = TagCreate(name="早餐")
    req2 = TagCreate(name="午餐")

    tag1 = await create_tag(db, user.id, req1)
    tag2 = await create_tag(db, user.id, req2)

    assert tag1.display_order == 0
    assert tag2.display_order == 1


@pytest.mark.asyncio
async def test_create_tag_duplicate_raises(db: AsyncSession, user: User):
    req = TagCreate(name="早餐")
    await create_tag(db, user.id, req)

    with pytest.raises(Exception):
        await create_tag(db, user.id, req)


@pytest.mark.asyncio
async def test_list_tags_with_stats(db: AsyncSession, user: User):
    req = TagCreate(name="早餐")
    await create_tag(db, user.id, req)

    result = await list_tags(db, user.id)

    assert len(result) == 1
    assert result[0].name == "早餐"
    assert result[0].transaction_count == 0


@pytest.mark.asyncio
async def test_update_tag(db: AsyncSession, user: User):
    req = TagCreate(name="早餐")
    tag = await create_tag(db, user.id, req)

    update_req = TagUpdate(name="早午餐")
    updated = await update_tag(db, user.id, tag.id, update_req)

    assert updated.name == "早午餐"


@pytest.mark.asyncio
async def test_update_tag_not_found(db: AsyncSession, user: User):
    update_req = TagUpdate(name="早午餐")

    with pytest.raises(Exception):
        await update_tag(db, user.id, 999, update_req)


@pytest.mark.asyncio
async def test_delete_tag(db: AsyncSession, user: User):
    req = TagCreate(name="早餐")
    tag = await create_tag(db, user.id, req)

    result = await delete_tag(db, user.id, tag.id)
    assert result["deleted"] is True

    remaining = await list_tags(db, user.id)
    assert len(remaining) == 0


@pytest.mark.asyncio
async def test_get_tags_by_category_empty(db: AsyncSession, user: User):
    result = await get_tags_by_category(db, user.id, 1)
    assert result == []
