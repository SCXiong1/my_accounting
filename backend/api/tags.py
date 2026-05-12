from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from middleware.jwt_auth import get_current_uid
from schemas.tag import TagCreate, TagUpdate, TagSortRequest
from services import tag_service

router = APIRouter(prefix="/api/v1/tags", tags=["标签"])


@router.get("")
async def list_tags(uid: int = Depends(get_current_uid), db: AsyncSession = Depends(get_db)):
    return await tag_service.list_tags(db, uid)


@router.post("")
async def create_tag(
    req: TagCreate,
    uid: int = Depends(get_current_uid),
    db: AsyncSession = Depends(get_db),
):
    tag = await tag_service.create_tag(db, uid, req)
    return {"id": tag.id, "name": tag.name, "display_order": tag.display_order, "expense_count": 0}


@router.put("/{tag_id}")
async def update_tag(
    tag_id: int,
    req: TagUpdate,
    uid: int = Depends(get_current_uid),
    db: AsyncSession = Depends(get_db),
):
    tag = await tag_service.update_tag(db, uid, tag_id, req)
    return {"id": tag.id, "name": tag.name, "display_order": tag.display_order, "expense_count": 0}


@router.delete("/{tag_id}")
async def delete_tag(
    tag_id: int,
    uid: int = Depends(get_current_uid),
    db: AsyncSession = Depends(get_db),
):
    return await tag_service.delete_tag(db, uid, tag_id)


@router.put("/sort")
async def sort_tags(
    req: TagSortRequest,
    uid: int = Depends(get_current_uid),
    db: AsyncSession = Depends(get_db),
):
    tags = await tag_service.sort_tags(db, uid, req)
    return [{"id": t.id, "name": t.name, "display_order": t.display_order, "expense_count": 0} for t in tags]
