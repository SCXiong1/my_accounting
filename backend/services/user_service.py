import time

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from middleware.error_handler import BadRequestException, NotFoundException
from models.user import User
from schemas.user import UpdateProfileRequest, UserResponse
from utils.security import create_token, hash_password, verify_password


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

    now = int(time.time())
    new_token = None

    if req.nickname is not None:
        user.nickname = req.nickname

    if req.password is not None:
        if not req.old_password:
            raise BadRequestException("修改密码需要提供旧密码")
        if not verify_password(req.old_password, user.password):
            raise BadRequestException("旧密码错误")
        user.password = hash_password(req.password)
        new_token = create_token(uid)

    user.updated_at = now
    await db.commit()

    result = {"user": UserResponse.model_validate(user)}
    if new_token:
        result["token"] = new_token
    return result
