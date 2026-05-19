from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from middleware.jwt_auth import get_current_uid
from schemas.tag import TagCreate, TagUpdate, TagSortRequest, TagResponse
from services import tag_service

router = APIRouter(prefix="/api/v1/tags", tags=["标签"])


@router.get("", response_model=list[TagResponse])
async def list_tags(uid: int = Depends(get_current_uid), db: AsyncSession = Depends(get_db)):
    return await tag_service.list_tags(db, uid)


@router.post("", response_model=TagResponse)
async def create_tag(
    req: TagCreate,
    uid: int = Depends(get_current_uid),
    db: AsyncSession = Depends(get_db),
):
    return await tag_service.create_tag(db, uid, req)


@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: int,
    req: TagUpdate,
    uid: int = Depends(get_current_uid),
    db: AsyncSession = Depends(get_db),
):
    return await tag_service.update_tag(db, uid, tag_id, req)


@router.delete("/{tag_id}")
async def delete_tag(
    tag_id: int,
    uid: int = Depends(get_current_uid),
    db: AsyncSession = Depends(get_db),
):
    return await tag_service.delete_tag(db, uid, tag_id)


@router.put("/sort", response_model=list[TagResponse])
async def sort_tags(
    req: TagSortRequest,
    uid: int = Depends(get_current_uid),
    db: AsyncSession = Depends(get_db),
):
    return await tag_service.sort_tags(db, uid, req)
