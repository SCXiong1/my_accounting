from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from middleware.jwt_auth import get_current_uid
from schemas.transaction import (
    BatchDeleteRequest,
    TransactionCreate,
    TransactionListResponse,
    TransactionResponse,
    TransactionUpdate,
)
from services import transaction_service

router = APIRouter(prefix="/api/v1/transactions", tags=["支出"])


@router.get("")
async def list_transactions(
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
) -> TransactionListResponse:
    return await transaction_service.list_transactions(
        db, uid, cursor=cursor, limit=limit,
        start_time=start_time, end_time=end_time,
        category_id=category_id, tag_id=tag_id, keyword=keyword,
        sort_by=sort_by, show_deleted=bool(deleted),
    )


@router.post("/batch-delete")
async def batch_delete_transactions(
    req: BatchDeleteRequest,
    uid: int = Depends(get_current_uid),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    deleted_count = await transaction_service.permanent_delete_transactions(db, uid, req.ids)
    return {"deleted_count": deleted_count}


@router.get("/{transaction_id}")
async def get_transaction(
    transaction_id: int,
    uid: int = Depends(get_current_uid),
    db: AsyncSession = Depends(get_db),
) -> TransactionResponse:
    return await transaction_service.get_transaction(db, uid, transaction_id)


@router.post("")
async def create_transaction(
    req: TransactionCreate,
    uid: int = Depends(get_current_uid),
    db: AsyncSession = Depends(get_db),
) -> TransactionResponse:
    return await transaction_service.create_transaction(db, uid, req)


@router.put("/{transaction_id}")
async def update_transaction(
    transaction_id: int,
    req: TransactionUpdate,
    uid: int = Depends(get_current_uid),
    db: AsyncSession = Depends(get_db),
) -> TransactionResponse:
    return await transaction_service.update_transaction(db, uid, transaction_id, req)


@router.post("/{transaction_id}/restore")
async def restore_transaction(
    transaction_id: int,
    uid: int = Depends(get_current_uid),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    return await transaction_service.restore_transaction(db, uid, transaction_id)


@router.delete("/{transaction_id}")
async def delete_transaction(
    transaction_id: int,
    uid: int = Depends(get_current_uid),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    return await transaction_service.delete_transaction(db, uid, transaction_id)
