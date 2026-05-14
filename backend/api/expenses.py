from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from middleware.jwt_auth import get_current_uid
from schemas.expense import ExpenseCreate, ExpenseUpdate
from services import expense_service

router = APIRouter(prefix="/api/v1/expenses", tags=["支出"])


@router.get("")
async def list_expenses(
    cursor: int | None = Query(default=None),
    limit: int = Query(default=20, le=100),
    start_time: int | None = Query(default=None),
    end_time: int | None = Query(default=None),
    category_id: int | None = Query(default=None),
    tag_id: int | None = Query(default=None),
    keyword: str | None = Query(default=None),
    sort_by: str = Query(default="time"),
    deleted: int = Query(default=0, le=1, ge=0),
    uid: int = Depends(get_current_uid),
    db: AsyncSession = Depends(get_db),
):
    return await expense_service.list_expenses(
        db, uid, cursor=cursor, limit=limit,
        start_time=start_time, end_time=end_time,
        category_id=category_id, tag_id=tag_id, keyword=keyword,
        sort_by=sort_by, show_deleted=bool(deleted),
    )


@router.get("/{expense_id}")
async def get_expense(
    expense_id: int,
    uid: int = Depends(get_current_uid),
    db: AsyncSession = Depends(get_db),
):
    return await expense_service.get_expense(db, uid, expense_id)


@router.post("")
async def create_expense(
    req: ExpenseCreate,
    uid: int = Depends(get_current_uid),
    db: AsyncSession = Depends(get_db),
):
    return await expense_service.create_expense(db, uid, req)


@router.put("/{expense_id}")
async def update_expense(
    expense_id: int,
    req: ExpenseUpdate,
    uid: int = Depends(get_current_uid),
    db: AsyncSession = Depends(get_db),
):
    return await expense_service.update_expense(db, uid, expense_id, req)


@router.post("/{expense_id}/restore")
async def restore_expense(
    expense_id: int,
    uid: int = Depends(get_current_uid),
    db: AsyncSession = Depends(get_db),
):
    return await expense_service.restore_expense(db, uid, expense_id)


@router.delete("/{expense_id}")
async def delete_expense(
    expense_id: int,
    uid: int = Depends(get_current_uid),
    db: AsyncSession = Depends(get_db),
):
    return await expense_service.delete_expense(db, uid, expense_id)
