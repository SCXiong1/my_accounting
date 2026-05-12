from fastapi import Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from utils.security import decode_token
from middleware.error_handler import UnauthorizedException

security = HTTPBearer(auto_error=False)


async def get_current_uid(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> int:
    token = None
    if credentials:
        token = credentials.credentials

    if not token:
        raise UnauthorizedException()

    uid = decode_token(token)
    if uid is None:
        raise UnauthorizedException()

    return uid
