from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from middleware.jwt_auth import get_current_uid
from schemas.category import CategoryCreate, CategoryUpdate, CategorySortRequest, CategoryResponse
from schemas.tag import TagResponse
from services import category_service
from services import tag_service

router = APIRouter(prefix="/api/v1/categories", tags=["分类"])


@router.get("", response_model=list[CategoryResponse])
async def list_categories(uid: int = Depends(get_current_uid), db: AsyncSession = Depends(get_db)):
    return await category_service.list_categories(db, uid)


@router.post("", response_model=CategoryResponse)
async def create_category(
    req: CategoryCreate,
    uid: int = Depends(get_current_uid),
    db: AsyncSession = Depends(get_db),
):
    return await category_service.create_category(db, uid, req)


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    req: CategoryUpdate,
    uid: int = Depends(get_current_uid),
    db: AsyncSession = Depends(get_db),
):
    return await category_service.update_category(db, uid, category_id, req)


@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    uid: int = Depends(get_current_uid),
    db: AsyncSession = Depends(get_db),
):
    return await category_service.delete_category(db, uid, category_id)


@router.put("/sort", response_model=list[CategoryResponse])
async def sort_categories(
    req: CategorySortRequest,
    uid: int = Depends(get_current_uid),
    db: AsyncSession = Depends(get_db),
):
    return await category_service.sort_categories(db, uid, req)


@router.get("/{category_id}/tags", response_model=list[TagResponse])
async def get_tags_by_category(
    category_id: int,
    uid: int = Depends(get_current_uid),
    db: AsyncSession = Depends(get_db),
):
    return await tag_service.get_tags_by_category(db, uid, category_id)
