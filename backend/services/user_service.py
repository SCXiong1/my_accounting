import time

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from middleware.error_handler import NotFoundException
from models.user import User
from schemas.user import UpdateProfileRequest, UserResponse


async def get_profile(db: AsyncSession, uid: int) -> UserResponse:
    result = await db.execute(select(User).where(User.id == uid))
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundException("用户")
    return UserResponse.model_validate(user)


async def update_profile(db: AsyncSession, uid: int, req: UpdateProfileRequest) -> dict:
    result = await db.execute(select(User).where(User.id == uid))
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundException("用户")

    if req.nickname is not None:
        user.nickname = req.nickname

    user.updated_at = int(time.time())
    await db.commit()

    return {"user": UserResponse.model_validate(user)}
