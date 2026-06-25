import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from api import api_router
from config import get
from database import init_db
from middleware.error_handler import AppException, app_exception_handler


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    await init_db()
    yield


app = FastAPI(title="个人记账", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    SessionMiddleware,
    secret_key=get("session.secret"),
    max_age=int(get("session.max_age", 86400)),
    session_cookie="session_id",
    same_site="lax",
    https_only=False,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get("cors.origins"),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppException, app_exception_handler)

app.include_router(api_router)


@app.get("/api/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}

# 生产模式：服务前端构建产物（Docker 环境 static/ 目录存在）
STATIC_DIR = "static"
if os.path.isdir(STATIC_DIR):
    app.mount("/assets", StaticFiles(directory=f"{STATIC_DIR}/assets"), name="assets")

    @app.get("/{path:path}")
    async def serve_spa(path: str) -> FileResponse:
        full = os.path.join(STATIC_DIR, path)
        if path and os.path.isfile(full) and not path.startswith("api"):
            return FileResponse(full)
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=get("server.host"),
        port=int(get("server.port")),
        reload=True,
    )
