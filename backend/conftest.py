import os
import pytest
import httpx

# 测试数据库隔离 — 必须在服务器启动时设置此环境变量：
#   APP_DATABASE_PATH=./data/test.db uvicorn main:app --host 0.0.0.0 --port 8080
os.environ.setdefault("APP_DATABASE_PATH", "./data/test.db")

BASE = "http://localhost:8080"


class TestState:
    """共享测试状态，替代全局变量"""
    def __init__(self):
        self.token_a: str | None = None
        self.token_b: str | None = None
        self.category_id: int | None = None
        self.tag_id: int | None = None
        self.expense_id: int | None = None


@pytest.fixture(scope="module")
def state():
    return TestState()


@pytest.fixture(scope="module")
def auth_headers(state: TestState):
    return {"Authorization": f"Bearer {state.token_a}"}
