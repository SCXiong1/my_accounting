"""回收站批量永久删除 API 集成测试

启动测试服务器：
  APP_DATABASE_PATH=./data/test.db uvicorn main:app --host 0.0.0.0 --port 8080
  pytest test_batch_delete.py -v
"""
import os

import httpx
import pytest

os.environ.setdefault("APP_DATABASE_PATH", "./data/test.db")

BASE = os.environ.get("TEST_BASE", "http://localhost:8080")


class _S:
    token: str | None = None
    cat_id: int | None = None
    tag_id: int | None = None
    expense_ids: list[int] = []


@pytest.fixture(scope="module")
def S():
    return _S()


def _auth(token: str | None) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ── Setup ──────────────────────────────────────────

def test_register(S: _S):
    resp = httpx.post(f"{BASE}/api/auth/register", json={
        "username": f"batch_del_{os.getpid()}", "password": "123456",
        "nickname": "批量删除测试", "email": f"batch_{os.getpid()}@test.com",
    })
    assert resp.status_code == 200
    S.token = resp.json()["token"]


def test_get_category(S: _S):
    resp = httpx.get(f"{BASE}/api/v1/categories", headers=_auth(S.token))
    assert resp.status_code == 200
    S.cat_id = resp.json()[0]["id"]


def test_create_tag(S: _S):
    resp = httpx.post(f"{BASE}/api/v1/tags", json={"name": "批量删除tag"}, headers=_auth(S.token))
    assert resp.status_code == 200
    S.tag_id = resp.json()["id"]


def test_create_expenses(S: _S):
    """创建 3 条支出"""
    ids = []
    for i in range(3):
        resp = httpx.post(f"{BASE}/api/v1/transactions", json={
            "amount": 1000 * (i + 1),
            "category_id": S.cat_id,
            "tag_ids": [S.tag_id],
            "transaction_time": 1700000000,
            "note": f"批量删除测试_{i}",
        }, headers=_auth(S.token))
        assert resp.status_code == 200
        ids.append(resp.json()["id"])
    S.expense_ids = ids


def test_soft_delete_expenses(S: _S):
    """软删除所有支出"""
    for eid in S.expense_ids:
        resp = httpx.delete(f"{BASE}/api/v1/transactions/{eid}", headers=_auth(S.token))
        assert resp.status_code == 200


# ── Tracer Bullet: 批量永久删除 ──────────────────

def test_batch_delete_requires_auth(S: _S):
    """未认证请求应返回 401/403"""
    resp = httpx.post(f"{BASE}/api/v1/transactions/batch-delete", json={"ids": [1]})
    assert resp.status_code in (401, 403)


def test_batch_delete_empty_ids(S: _S):
    """空 ID 列表应返回 422"""
    resp = httpx.post(f"{BASE}/api/v1/transactions/batch-delete", json={"ids": []}, headers=_auth(S.token))
    assert resp.status_code == 422


def test_batch_delete_permanent(S: _S):
    """批量永久删除应成功"""
    resp = httpx.post(f"{BASE}/api/v1/transactions/batch-delete", json={"ids": S.expense_ids}, headers=_auth(S.token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["deleted_count"] == 3


def test_batch_delete_verifies_gone(S: _S):
    """删除后记录应不可恢复"""
    for eid in S.expense_ids:
        resp = httpx.post(f"{BASE}/api/v1/transactions/{eid}/restore", headers=_auth(S.token))
        assert resp.status_code == 404


def test_batch_delete_only_own_expenses(S: _S):
    """不能删除别人的支出"""
    # 注册另一个用户
    resp = httpx.post(f"{BASE}/api/auth/register", json={
        "username": f"batch_other_{os.getpid()}", "password": "123456",
        "nickname": "其他用户", "email": f"batch_other_{os.getpid()}@test.com",
    })
    assert resp.status_code == 200
    other_token = resp.json()["token"]

    # 获取其他用户的分类
    resp = httpx.get(f"{BASE}/api/v1/categories", headers=_auth(other_token))
    assert resp.status_code == 200
    other_cat_id = resp.json()[0]["id"]

    # 创建一条支出（用其他用户的分类）
    resp = httpx.post(f"{BASE}/api/v1/transactions", json={
        "amount": 9999, "category_id": other_cat_id, "tag_ids": [],
        "transaction_time": 1700000000, "note": "其他用户的支出",
    }, headers=_auth(other_token))
    assert resp.status_code == 200
    other_expense_id = resp.json()["id"]

    # 软删除
    resp = httpx.delete(f"{BASE}/api/v1/transactions/{other_expense_id}", headers=_auth(other_token))
    assert resp.status_code == 200

    # 尝试用 S.token 永久删除
    resp = httpx.post(
        f"{BASE}/api/v1/transactions/batch-delete",
        json={"ids": [other_expense_id]},
        headers=_auth(S.token),
    )
    assert resp.status_code == 200
    assert resp.json()["deleted_count"] == 0
