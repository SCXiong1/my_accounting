"""API 集成测试

启动测试服务器：
  APP_DATABASE_PATH=./data/test.db uvicorn main:app --host 0.0.0.0 --port 8080
  pytest test_api.py -v
"""
import os
import time

import httpx
import pytest

os.environ.setdefault("APP_DATABASE_PATH", "./data/test.db")

BASE = os.environ.get("TEST_BASE", "http://localhost:8080")


class _S:
    """模块级共享状态，替代全局变量"""
    token_a: str | None = None
    token_b: str | None = None
    category_id: int | None = None
    tag_id: int | None = None
    expense_id: int | None = None


@pytest.fixture(scope="module")
def S():
    return _S()


def _auth(token: str | None) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ── 认证 ──────────────────────────────────────────

def test_register_a(S: _S):
    resp = httpx.post(f"{BASE}/api/auth/register", json={
        "username": "testuser_a", "password": "123456",
        "nickname": "用户A", "email": "a@test.com",
    })
    assert resp.status_code == 200, f"Register A failed: {resp.text}"
    data = resp.json()
    S.token_a = data["token"]
    assert "token" in data
    assert data["user"]["username"] == "testuser_a"
    print("  [OK] 注册用户A")


def test_register_b(S: _S):
    resp = httpx.post(f"{BASE}/api/auth/register", json={
        "username": "testuser_b", "password": "123456",
        "nickname": "用户B", "email": "b@test.com",
    })
    assert resp.status_code == 200, f"Register B failed: {resp.text}"
    S.token_b = resp.json()["token"]
    print("  [OK] 注册用户B")


def test_register_duplicate():
    resp = httpx.post(f"{BASE}/api/auth/register", json={
        "username": "testuser_a", "password": "123456",
        "nickname": "dup", "email": "dup@test.com",
    })
    assert resp.status_code == 400
    print("  [OK] 重复注册被拒绝")


def test_login(S: _S):
    resp = httpx.post(f"{BASE}/api/auth/login", json={
        "username": "testuser_a", "password": "123456"
    })
    assert resp.status_code == 200
    S.token_a = resp.json()["token"]
    print("  [OK] 登录成功")


def test_login_wrong_password():
    resp = httpx.post(f"{BASE}/api/auth/login", json={
        "username": "testuser_a", "password": "wrong"
    })
    assert resp.status_code == 401
    print("  [OK] 错误密码被拒绝")


def test_refresh_token(S: _S):
    resp = httpx.post(f"{BASE}/api/auth/refresh", headers=_auth(S.token_a))
    assert resp.status_code == 200
    assert "token" in resp.json()
    print("  [OK] 刷新令牌成功")


# ── 分类 ──────────────────────────────────────────

def test_preset_categories(S: _S):
    resp = httpx.get(f"{BASE}/api/v1/categories", headers=_auth(S.token_a))
    assert resp.status_code == 200
    cats = resp.json()
    assert len(cats) == 8, f"预期 8 个预设分类，实际 {len(cats)}"
    names = [c["name"] for c in cats]
    assert "餐饮" in names
    assert "交通" in names
    print(f"  [OK] 预设分类检查通过: {names}")


def test_create_category(S: _S):
    resp = httpx.post(f"{BASE}/api/v1/categories",
                      json={"name": "宠物", "icon": "🐱", "color": "#FF4081"},
                      headers=_auth(S.token_a))
    assert resp.status_code == 200, f"Create category failed: {resp.text}"
    S.category_id = resp.json()["id"]
    print(f"  [OK] 创建分类: 宠物 (id={S.category_id})")


# ── 标签 ──────────────────────────────────────────

def test_create_tag(S: _S):
    resp = httpx.post(f"{BASE}/api/v1/tags",
                      json={"name": "午餐"},
                      headers=_auth(S.token_a))
    assert resp.status_code == 200, f"Create tag failed: {resp.text}"
    S.tag_id = resp.json()["id"]
    print(f"  [OK] 创建标签: 午餐 (id={S.tag_id})")


def test_create_tag2(S: _S):
    resp = httpx.post(f"{BASE}/api/v1/tags",
                      json={"name": "工作餐"},
                      headers=_auth(S.token_a))
    assert resp.status_code == 200
    print(f"  [OK] 创建标签: 工作餐 (id={resp.json()['id']})")


def test_create_tag_duplicate(S: _S):
    """同名标签应被拒绝"""
    resp = httpx.post(f"{BASE}/api/v1/tags",
                      json={"name": "午餐"},
                      headers=_auth(S.token_a))
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    print("  [OK] 同名标签创建被拒绝")


# ── 支出 ──────────────────────────────────────────

def test_create_expense(S: _S):
    now = int(time.time())
    resp = httpx.post(f"{BASE}/api/v1/transactions",
                      json={
                          "amount": 3500,
                          "category_id": S.category_id,
                          "tag_ids": [S.tag_id],
                          "transaction_time": now,
                          "note": "给猫咪买猫粮"
                      },
                      headers=_auth(S.token_a))
    assert resp.status_code == 200, f"Create expense failed: {resp.text}"
    S.expense_id = resp.json()["id"]
    print(f"  [OK] 创建支出: id={S.expense_id}, amount=3500")


def test_list_expenses(S: _S):
    resp = httpx.get(f"{BASE}/api/v1/transactions?limit=10",
                     headers=_auth(S.token_a))
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["amount"] == 3500
    assert data["items"][0]["note"] == "给猫咪买猫粮"
    assert len(data["items"][0]["tags"]) > 0
    print(f"  [OK] 支出列表: {data['total']} 条记录")


def test_expense_filter_by_tag(S: _S):
    resp = httpx.get(f"{BASE}/api/v1/transactions?tag_id={S.tag_id}",
                     headers=_auth(S.token_a))
    assert resp.status_code == 200
    assert resp.json()["total"] == 1
    print("  [OK] 按标签筛选正常")


def test_expense_filter_by_keyword(S: _S):
    resp = httpx.get(f"{BASE}/api/v1/transactions?keyword=猫粮",
                     headers=_auth(S.token_a))
    assert resp.status_code == 200
    assert resp.json()["total"] == 1
    print("  [OK] 按关键词筛选正常")


def test_update_expense(S: _S):
    resp = httpx.put(f"{BASE}/api/v1/transactions/{S.expense_id}",
                     json={"note": "给猫咪买进口猫粮"},
                     headers=_auth(S.token_a))
    assert resp.status_code == 200
    assert resp.json()["note"] == "给猫咪买进口猫粮"
    print("  [OK] 修改支出成功")


# ── 统计 ──────────────────────────────────────────

def test_statistics_overview(S: _S):
    resp = httpx.get(f"{BASE}/api/v1/statistics/overview",
                     headers=_auth(S.token_a))
    assert resp.status_code == 200
    data = resp.json()
    assert data["today"] >= 0
    assert data["this_year"] >= 0
    print(f"  [OK] 概览统计: {data}")


def test_statistics_by_category(S: _S):
    resp = httpx.get(f"{BASE}/api/v1/statistics/by_category",
                     headers=_auth(S.token_a))
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) > 0
    print(f"  [OK] 按分类统计: {len(data)} 个分类有数据")


def test_statistics_by_tag(S: _S):
    resp = httpx.get(f"{BASE}/api/v1/statistics/by_tag",
                     headers=_auth(S.token_a))
    assert resp.status_code == 200
    print(f"  [OK] 按标签统计: {len(resp.json())} 个标签")


def test_statistics_monthly(S: _S):
    resp = httpx.get(f"{BASE}/api/v1/statistics/monthly",
                     headers=_auth(S.token_a))
    assert resp.status_code == 200
    print(f"  [OK] 月度统计: {len(resp.json())} 个月")


# ── 权限与删除 ────────────────────────────────────

def test_user_isolation(S: _S):
    resp = httpx.get(f"{BASE}/api/v1/transactions",
                     headers=_auth(S.token_b))
    assert resp.status_code == 200
    assert resp.json()["total"] == 0
    print("  [OK] 用户隔离: 用户B看不到用户A的数据")


def test_delete_category_blocked(S: _S):
    resp = httpx.delete(f"{BASE}/api/v1/categories/{S.category_id}",
                        headers=_auth(S.token_a))
    assert resp.status_code == 400
    print("  [OK] 有支出的分类删除被阻止")


def test_delete_expense(S: _S):
    resp = httpx.delete(f"{BASE}/api/v1/transactions/{S.expense_id}",
                        headers=_auth(S.token_a))
    assert resp.status_code == 200
    assert resp.json()["deleted"] is True
    print("  [OK] 删除支出成功")


def test_restore_expense(S: _S):
    """恢复已删除支出，标签应一并恢复"""
    resp = httpx.post(f"{BASE}/api/v1/transactions/{S.expense_id}/restore",
                      headers=_auth(S.token_a))
    assert resp.status_code == 200, f"Restore failed: {resp.text}"
    # 验证标签已恢复
    detail = httpx.get(f"{BASE}/api/v1/transactions/{S.expense_id}",
                       headers=_auth(S.token_a))
    assert detail.status_code == 200
    assert len(detail.json()["tags"]) > 0, "标签未恢复"
    print("  [OK] 恢复支出成功，标签已恢复")


# ── 用户 ──────────────────────────────────────────

def test_profile(S: _S):
    resp = httpx.get(f"{BASE}/api/v1/user/profile",
                     headers=_auth(S.token_a))
    assert resp.status_code == 200
    assert resp.json()["user"]["username"] == "testuser_a"
    print("  [OK] 获取个人信息成功")


def test_update_profile(S: _S):
    resp = httpx.put(f"{BASE}/api/v1/user/profile",
                     json={"nickname": "小明"},
                     headers=_auth(S.token_a))
    assert resp.status_code == 200
    assert resp.json()["user"]["nickname"] == "小明"
    print("  [OK] 修改昵称成功")


# ── 手动执行入口 ──────────────────────────────────

if __name__ == "__main__":
    _state = _S()
    tests = [
        test_register_a, test_register_b, test_register_duplicate,
        test_login, test_login_wrong_password, test_refresh_token,
        test_preset_categories, test_create_category,
        test_create_tag, test_create_tag2, test_create_tag_duplicate,
        test_create_expense, test_list_expenses,
        test_expense_filter_by_tag, test_expense_filter_by_keyword,
        test_update_expense,
        test_statistics_overview, test_statistics_by_category,
        test_statistics_by_tag, test_statistics_monthly,
        test_user_isolation, test_delete_category_blocked,
        test_delete_expense, test_restore_expense,
        test_profile, test_update_profile,
    ]

    passed = 0
    failed = 0
    for test in tests:
        try:
            test(_state)
            passed += 1
        except Exception as e:
            failed += 1
            print(f"  [FAIL] {test.__name__}: {e}")

    print(f"\n{'='*40}")
    print(f"结果: {passed} 通过, {failed} 失败, 共 {len(tests)} 项")
    print(f"{'='*40}")
