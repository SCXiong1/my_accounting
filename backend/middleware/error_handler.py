from fastapi import Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail


class NotFoundException(AppException):
    def __init__(self, entity: str = "资源"):
        super().__init__(404, f"{entity}不存在")


class ForbiddenException(AppException):
    def __init__(self):
        super().__init__(403, "无权操作此资源")


class BadRequestException(AppException):
    def __init__(self, detail: str):
        super().__init__(400, detail)


class UnauthorizedException(AppException):
    def __init__(self, detail: str = "未登录或令牌已过期"):
        super().__init__(401, detail)


async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
