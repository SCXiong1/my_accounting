from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from middleware.jwt_auth import get_current_uid
from services import statistics_service

router = APIRouter(prefix="/api/v1/statistics", tags=["统计"])


def _parse_ids(s: str | None) -> list[int] | None:
    if not s:
        return None
    ids = [int(x) for x in s.split(",") if x.strip()]
    return ids if ids else None


@router.get("/overview")
async def overview(uid: int = Depends(get_current_uid), db: AsyncSession = Depends(get_db)):
    return await statistics_service.overview(db, uid)


@router.get("/by_category")
async def by_category(
    start_time: int | None = Query(default=None),
    end_time: int | None = Query(default=None),
    tag_ids: str | None = Query(default=None),
    uid: int = Depends(get_current_uid),
    db: AsyncSession = Depends(get_db),
):
    return await statistics_service.by_category(db, uid, start_time, end_time, _parse_ids(tag_ids))


@router.get("/by_tag")
async def by_tag(
    start_time: int | None = Query(default=None),
    end_time: int | None = Query(default=None),
    category_ids: str | None = Query(default=None),
    uid: int = Depends(get_current_uid),
    db: AsyncSession = Depends(get_db),
):
    return await statistics_service.by_tag(db, uid, start_time, end_time, _parse_ids(category_ids))


@router.get("/monthly")
async def monthly(
    start_year: int | None = Query(default=None),
    start_month: int | None = Query(default=None),
    end_year: int | None = Query(default=None),
    end_month: int | None = Query(default=None),
    category_ids: str | None = Query(default=None),
    tag_ids: str | None = Query(default=None),
    uid: int = Depends(get_current_uid),
    db: AsyncSession = Depends(get_db),
):
    return await statistics_service.monthly(
        db, uid, start_year, start_month, end_year, end_month,
        _parse_ids(category_ids), _parse_ids(tag_ids),
    )
