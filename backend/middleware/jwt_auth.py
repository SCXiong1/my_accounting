from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from middleware.error_handler import UnauthorizedException
from utils.security import decode_token

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
