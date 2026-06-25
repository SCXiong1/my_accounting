from fastapi import Request

from middleware.error_handler import UnauthorizedException


async def get_current_uid(request: Request) -> int:
    uid = request.session.get("uid")
    if not uid:
        raise UnauthorizedException()
    return int(uid)
