from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from middleware.jwt_auth import get_current_uid
from schemas.auth import RegisterRequest, LoginRequest, ForgotPasswordRequest
from services import auth_service

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/register")
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.register(db, req)


@router.post("/login")
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.login(db, req)


@router.post("/forgot-password")
async def forgot_password(req: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.forgot_password(db, req.username, req.email, req.new_password)


@router.post("/refresh")
async def refresh(uid: int = Depends(get_current_uid)):
    return await auth_service.refresh_token(uid)
