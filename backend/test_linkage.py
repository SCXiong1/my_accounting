"""分类标签联动 API 集成测试

启动测试服务器：
  APP_DATABASE_PATH=./data/test.db uvicorn main:app --host 0.0.0.0 --port 8080
  pytest test_linkage.py -v
"""
import os
import httpx
import pytest

os.environ.setdefault("APP_DATABASE_PATH", "./data/test.db")

BASE = os.environ.get("TEST_BASE", "http://localhost:8080")


class _S:
    token: str | None = None
    cat_food: int | None = None
    cat_transport: int | None = None
    tag_lunch: int | None = None
    tag_taxi: int | None = None
    tag_shopping: int | None = None


@pytest.fixture(scope="module")
def S():
    return _S()


def _auth(token: str | None) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ── Setup ──────────────────────────────────────────

def test_register(S: _S):
    resp = httpx.post(f"{BASE}/api/auth/register", json={
        "username": f"linkage_test_{os.getpid()}", "password": "123456",
        "nickname": "联动测试", "email": f"linkage_{os.getpid()}@test.com",
    })
    assert resp.status_code == 200, f"Register failed: {resp.text}"
    S.token = resp.json()["token"]


def test_get_categories(S: _S):
    resp = httpx.get(f"{BASE}/api/v1/categories", headers=_auth(S.token))
    assert resp.status_code == 200
    cats = resp.json()
    cat_map = {c["name"]: c["id"] for c in cats}
    S.cat_food = cat_map.get("餐饮")
    S.cat_transport = cat_map.get("交通")
    assert S.cat_food is not None, "预设分类'餐饮'不存在"
    assert S.cat_transport is not None, "预设分类'交通'不存在"


def test_create_tags(S: _S):
    for name, attr in [("午餐tag", "tag_lunch"), ("打车tag", "tag_taxi"), ("购物tag", "tag_shopping")]:
        resp = httpx.post(f"{BASE}/api/v1/tags", json={"name": name}, headers=_auth(S.token))
        assert resp.status_code == 200, f"Create tag '{name}' failed: {resp.text}"
        setattr(S, attr, resp.json()["id"])


def test_create_expense_with_food_and_lunch(S: _S):
    """创建一条 餐饮+午餐 的支出"""
    resp = httpx.post(f"{BASE}/api/v1/expenses", json={
        "amount": 3500,
        "category_id": S.cat_food,
        "tag_ids": [S.tag_lunch],
        "transaction_time": 1700000000,
        "note": "联动测试-午餐",
    }, headers=_auth(S.token))
    assert resp.status_code == 200, f"Create expense failed: {resp.text}"


def test_create_expense_with_transport_and_taxi(S: _S):
    """创建一条 交通+打车 的支出"""
    resp = httpx.post(f"{BASE}/api/v1/expenses", json={
        "amount": 15000,
        "category_id": S.cat_transport,
        "tag_ids": [S.tag_taxi],
        "transaction_time": 1700000000,
        "note": "联动测试-打车",
    }, headers=_auth(S.token))
    assert resp.status_code == 200


# ── Tracer Bullet #1: 分类下的标签 ──────────────────

def test_get_tags_by_category_food(S: _S):
    """餐饮分类下应该只有午餐tag，没有打车tag和购物tag"""
    resp = httpx.get(f"{BASE}/api/v1/categories/{S.cat_food}/tags", headers=_auth(S.token))
    assert resp.status_code == 200, f"API not found: {resp.status_code}"
    tags = resp.json()
    tag_ids = [t["id"] for t in tags]
    assert S.tag_lunch in tag_ids, "餐饮分类下应包含午餐tag"
    assert S.tag_taxi not in tag_ids, "餐饮分类下不应包含打车tag"
    assert S.tag_shopping not in tag_ids, "餐饮分类下不应包含购物tag"


def test_get_tags_by_category_transport(S: _S):
    """交通分类下应该只有打车tag"""
    resp = httpx.get(f"{BASE}/api/v1/categories/{S.cat_transport}/tags", headers=_auth(S.token))
    assert resp.status_code == 200
    tags = resp.json()
    tag_ids = [t["id"] for t in tags]
    assert S.tag_taxi in tag_ids, "交通分类下应包含打车tag"
    assert S.tag_lunch not in tag_ids, "交通分类下不应包含午餐tag"


# ── Tracer Bullet #2: 标签下的分类 ──────────────────

def test_get_categories_by_tag_lunch(S: _S):
    """午餐tag下应该只有餐饮分类"""
    resp = httpx.get(f"{BASE}/api/v1/tags/{S.tag_lunch}/categories", headers=_auth(S.token))
    assert resp.status_code == 200, f"API not found: {resp.status_code}"
    cats = resp.json()
    cat_ids = [c["id"] for c in cats]
    assert S.cat_food in cat_ids, "午餐tag下应包含餐饮分类"
    assert S.cat_transport not in cat_ids, "午餐tag下不应包含交通分类"


def test_get_categories_by_tag_shopping(S: _S):
    """购物tag未被任何支出使用过，应返回空列表"""
    resp = httpx.get(f"{BASE}/api/v1/tags/{S.tag_shopping}/categories", headers=_auth(S.token))
    assert resp.status_code == 200
    cats = resp.json()
    assert len(cats) == 0, "未使用的标签应返回空分类列表"


# ── 用户隔离 ──────────────────────────────────────

def test_other_user_cannot_see_linkage(S: _S):
    """未认证请求应返回 401/403"""
    resp = httpx.get(f"{BASE}/api/v1/categories/{S.cat_food}/tags")
    assert resp.status_code in (401, 403)
