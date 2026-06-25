import time

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from middleware.error_handler import BadRequestException, UnauthorizedException
from models.user import User
from schemas.auth import AuthResponse, LoginRequest
from schemas.user import UserResponse
from utils.security import check_rate_limit, hash_pin, increment_attempts, reset_attempts, verify_pin

SECURITY_QUESTION = "小1是谁？"
SECURITY_ANSWER = "小1"


async def login(db: AsyncSession, req: LoginRequest, session: dict) -> AuthResponse:
    result = await db.execute(select(User).where(User.username == req.username))
    user = result.scalar_one_or_none()

    if not user:
        raise UnauthorizedException("用户名或PIN码错误")

    check_rate_limit(user)

    if not verify_pin(req.pin, user.password):
        increment_attempts(user)
        await db.commit()
        raise UnauthorizedException("用户名或PIN码错误")

    reset_attempts(user)
    user.updated_at = int(time.time())
    await db.commit()

    session["uid"] = user.id

    user_resp = UserResponse.model_validate(user)
    return AuthResponse(user=user_resp)


async def verify_security_answer(username: str, answer: str) -> dict:
    if answer != SECURITY_ANSWER:
        raise BadRequestException("安全问题答案错误")
    return {"message": "验证成功"}


async def reset_pin(db: AsyncSession, username: str, answer: str, new_pin: str) -> dict:
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    if not user:
        raise BadRequestException("用户名不存在")

    if answer != SECURITY_ANSWER:
        raise BadRequestException("安全问题答案错误")

    user.password = hash_pin(new_pin)
    user.pin_changed = 1
    user.updated_at = int(time.time())
    reset_attempts(user)
    await db.commit()

    return {"message": "PIN码重置成功"}


async def change_pin(db: AsyncSession, uid: int, current_pin: str, new_pin: str) -> dict:
    result = await db.execute(select(User).where(User.id == uid))
    user = result.scalar_one_or_none()

    if not user:
        raise BadRequestException("用户不存在")

    if not verify_pin(current_pin, user.password):
        raise BadRequestException("当前PIN码错误")

    user.password = hash_pin(new_pin)
    user.pin_changed = 1
    user.updated_at = int(time.time())
    reset_attempts(user)
    await db.commit()

    return {"message": "PIN码修改成功"}
