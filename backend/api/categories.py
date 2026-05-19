from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from middleware.jwt_auth import get_current_uid
from schemas.category import CategoryCreate, CategoryUpdate, CategorySortRequest, CategoryResponse
from services import category_service

router = APIRouter(prefix="/api/v1/categories", tags=["分类"])


@router.get("")
async def list_categories(uid: int = Depends(get_current_uid), db: AsyncSession = Depends(get_db)):
    return await category_service.list_categories(db, uid)


@router.post("")
async def create_category(
    req: CategoryCreate,
    uid: int = Depends(get_current_uid),
    db: AsyncSession = Depends(get_db),
):
    cat = await category_service.create_category(db, uid, req)
    return CategoryResponse.model_validate(cat)


@router.put("/{category_id}")
async def update_category(
    category_id: int,
    req: CategoryUpdate,
    uid: int = Depends(get_current_uid),
    db: AsyncSession = Depends(get_db),
):
    cat = await category_service.update_category(db, uid, category_id, req)
    return CategoryResponse.model_validate(cat)


@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    uid: int = Depends(get_current_uid),
    db: AsyncSession = Depends(get_db),
):
    return await category_service.delete_category(db, uid, category_id)


@router.put("/sort")
async def sort_categories(
    req: CategorySortRequest,
    uid: int = Depends(get_current_uid),
    db: AsyncSession = Depends(get_db),
):
    cats = await category_service.sort_categories(db, uid, req)
    return [CategoryResponse.model_validate(c) for c in cats]
