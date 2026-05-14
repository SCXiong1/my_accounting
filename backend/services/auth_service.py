import time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.user import User
from models.expense_category import ExpenseCategory
from utils.security import hash_password, verify_password, create_token
from middleware.error_handler import BadRequestException, UnauthorizedException
from schemas.auth import RegisterRequest, LoginRequest, AuthResponse
from schemas.user import UserResponse

PRESET_CATEGORIES = [
    {"name": "餐饮", "icon": "🍽️", "color": "#FF5722"},
    {"name": "交通", "icon": "🚗", "color": "#2196F3"},
    {"name": "购物", "icon": "🛒", "color": "#FF9800"},
    {"name": "住房", "icon": "🏠", "color": "#795548"},
    {"name": "娱乐", "icon": "🎮", "color": "#9C27B0"},
    {"name": "医疗", "icon": "💊", "color": "#4CAF50"},
    {"name": "教育", "icon": "📚", "color": "#009688"},
    {"name": "其他", "icon": "📦", "color": "#607D8B"},
]


async def register(db: AsyncSession, req: RegisterRequest) -> AuthResponse:
    result = await db.execute(select(User).where(User.username == req.username))
    if result.scalar_one_or_none():
        raise BadRequestException("用户名已存在")

    now = int(time.time())
    user = User(
        username=req.username,
        email=req.email,
        password=hash_password(req.password),
        nickname=req.nickname or req.username,
        created_at=now,
        updated_at=now,
    )
    db.add(user)
    await db.flush()

    for i, cat in enumerate(PRESET_CATEGORIES):
        db.add(ExpenseCategory(
            uid=user.id,
            name=cat["name"],
            icon=cat["icon"],
            color=cat["color"],
            display_order=i,
            created_at=now,
            updated_at=now,
        ))

    await db.commit()

    token = create_token(user.id)
    user_resp = UserResponse.model_validate(user)
    return AuthResponse(token=token, user=user_resp)


async def login(db: AsyncSession, req: LoginRequest) -> AuthResponse:
    result = await db.execute(select(User).where(User.username == req.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(req.password, user.password):
        raise UnauthorizedException("用户名或密码错误")

    token = create_token(user.id)
    user_resp = UserResponse.model_validate(user)
    return AuthResponse(token=token, user=user_resp)


async def forgot_password(db: AsyncSession, username: str, email: str, new_password: str) -> dict:
    """忘记密码：验证用户名+邮箱后设置新密码"""
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        raise BadRequestException("用户名不存在")

    if user.email != email:
        raise BadRequestException("邮箱不匹配，无法验证身份")

    user.password = hash_password(new_password)
    user.updated_at = int(time.time())
    await db.commit()

    return {"message": "密码重置成功，请使用新密码登录"}


async def refresh_token(uid: int) -> dict:
    return {"token": create_token(uid)}
