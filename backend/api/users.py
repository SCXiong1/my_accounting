from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from middleware.jwt_auth import get_current_uid
from schemas.user import UpdateProfileRequest
from services import user_service

router = APIRouter(prefix="/api/v1/user", tags=["用户"])


@router.get("/profile")
async def get_profile(uid: int = Depends(get_current_uid), db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    return {"user": await user_service.get_profile(db, uid)}


@router.put("/profile")
async def update_profile(
    req: UpdateProfileRequest,
    uid: int = Depends(get_current_uid),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    return await user_service.update_profile(db, uid, req)
