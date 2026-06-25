from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from middleware.jwt_auth import get_current_uid
from schemas.auth import (
    AuthResponse,
    ChangePinRequest,
    LoginRequest,
    ResetPinRequest,
    SecurityQuestionResponse,
    SecurityVerifyRequest,
)
from services import auth_service

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/login", response_model=AuthResponse)
async def login(
    req: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> AuthResponse:
    return await auth_service.login(db, req, request.session)


@router.post("/logout")
async def logout(request: Request) -> dict[str, str]:
    request.session.clear()
    return {"message": "已退出登录"}


@router.get("/security-question", response_model=SecurityQuestionResponse)
async def get_security_question() -> SecurityQuestionResponse:
    return SecurityQuestionResponse(question=auth_service.SECURITY_QUESTION)


@router.post("/verify-security")
async def verify_security(req: SecurityVerifyRequest) -> dict[str, str]:
    return await auth_service.verify_security_answer(req.username, req.answer)


@router.post("/reset-pin")
async def reset_pin(req: ResetPinRequest, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    return await auth_service.reset_pin(db, req.username, req.answer, req.new_pin)


@router.post("/change-pin")
async def change_pin(
    req: ChangePinRequest,
    uid: int = Depends(get_current_uid),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    return await auth_service.change_pin(db, uid, req.current_pin, req.new_pin)
