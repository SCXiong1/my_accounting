"""API 集成测试"""
import httpx
import time

BASE = "http://localhost:8080"
TOKEN_A = None
TOKEN_B = None
CATEGORY_ID = None
TAG_ID = None
EXPENSE_ID = None


def test_register_a():
    global TOKEN_A
    resp = httpx.post(f"{BASE}/api/auth/register", json={
        "username": "testuser_a", "password": "123456", "nickname": "用户A"
    })
    assert resp.status_code == 200, f"Register A failed: {resp.text}"
    data = resp.json()
    TOKEN_A = data["token"]
    assert "token" in data
    assert data["user"]["username"] == "testuser_a"
    print(f"  [OK] 注册用户A")


def test_register_b():
    global TOKEN_B
    resp = httpx.post(f"{BASE}/api/auth/register", json={
        "username": "testuser_b", "password": "123456", "nickname": "用户B"
    })
    assert resp.status_code == 200, f"Register B failed: {resp.text}"
    TOKEN_B = resp.json()["token"]
    print(f"  [OK] 注册用户B")


def test_register_duplicate():
    resp = httpx.post(f"{BASE}/api/auth/register", json={
        "username": "testuser_a", "password": "123456", "nickname": "dup"
    })
    assert resp.status_code == 400
    print(f"  [OK] 重复注册被拒绝")


def test_login():
    global TOKEN_A
    resp = httpx.post(f"{BASE}/api/auth/login", json={
        "username": "testuser_a", "password": "123456"
    })
    assert resp.status_code == 200
    TOKEN_A = resp.json()["token"]
    print(f"  [OK] 登录成功")


def test_login_wrong_password():
    resp = httpx.post(f"{BASE}/api/auth/login", json={
        "username": "testuser_a", "password": "wrong"
    })
    assert resp.status_code == 401
    print(f"  [OK] 错误密码被拒绝")


def test_refresh_token():
    resp = httpx.post(f"{BASE}/api/auth/refresh", headers={"Authorization": f"Bearer {TOKEN_A}"})
    assert resp.status_code == 200
    assert "token" in resp.json()
    print(f"  [OK] 刷新令牌成功")


def test_preset_categories():
    resp = httpx.get(f"{BASE}/api/v1/categories", headers={"Authorization": f"Bearer {TOKEN_A}"})
    assert resp.status_code == 200
    cats = resp.json()
    assert len(cats) == 8, f"预期 8 个预设分类，实际 {len(cats)}"
    names = [c["name"] for c in cats]
    assert "餐饮" in names
    assert "交通" in names
    print(f"  [OK] 预设分类检查通过: {names}")


def test_create_category():
    global CATEGORY_ID
    resp = httpx.post(f"{BASE}/api/v1/categories",
                      json={"name": "宠物", "icon": "🐱", "color": "#FF4081"},
                      headers={"Authorization": f"Bearer {TOKEN_A}"})
    assert resp.status_code == 200, f"Create category failed: {resp.text}"
    CATEGORY_ID = resp.json()["id"]
    print(f"  [OK] 创建分类: 宠物 (id={CATEGORY_ID})")


def test_create_tag():
    global TAG_ID
    resp = httpx.post(f"{BASE}/api/v1/tags",
                      json={"name": "午餐"},
                      headers={"Authorization": f"Bearer {TOKEN_A}"})
    assert resp.status_code == 200, f"Create tag failed: {resp.text}"
    TAG_ID = resp.json()["id"]
    print(f"  [OK] 创建标签: 午餐 (id={TAG_ID})")


def test_create_tag2():
    resp = httpx.post(f"{BASE}/api/v1/tags",
                      json={"name": "工作餐"},
                      headers={"Authorization": f"Bearer {TOKEN_A}"})
    assert resp.status_code == 200
    print(f"  [OK] 创建标签: 工作餐 (id={resp.json()['id']})")


def test_create_expense():
    global EXPENSE_ID
    now = int(time.time())
    resp = httpx.post(f"{BASE}/api/v1/expenses",
                      json={
                          "amount": 3500,  # 35元
                          "category_id": CATEGORY_ID,
                          "tag_ids": [TAG_ID],
                          "transaction_time": now,
                          "note": "给猫咪买猫粮"
                      },
                      headers={"Authorization": f"Bearer {TOKEN_A}"})
    assert resp.status_code == 200, f"Create expense failed: {resp.text}"
    EXPENSE_ID = resp.json()["id"]
    print(f"  [OK] 创建支出: id={EXPENSE_ID}, amount=3500")


def test_list_expenses():
    resp = httpx.get(f"{BASE}/api/v1/expenses?limit=10",
                     headers={"Authorization": f"Bearer {TOKEN_A}"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["amount"] == 3500
    assert data["items"][0]["note"] == "给猫咪买猫粮"
    assert len(data["items"][0]["tags"]) > 0
    print(f"  [OK] 支出列表: {data['total']} 条记录")


def test_expense_filter_by_tag():
    resp = httpx.get(f"{BASE}/api/v1/expenses?tag_id={TAG_ID}",
                     headers={"Authorization": f"Bearer {TOKEN_A}"})
    assert resp.status_code == 200
    assert resp.json()["total"] == 1
    print(f"  [OK] 按标签筛选正常")


def test_expense_filter_by_keyword():
    resp = httpx.get(f"{BASE}/api/v1/expenses?keyword=猫粮",
                     headers={"Authorization": f"Bearer {TOKEN_A}"})
    assert resp.status_code == 200
    assert resp.json()["total"] == 1
    print(f"  [OK] 按关键词筛选正常")


def test_update_expense():
    resp = httpx.put(f"{BASE}/api/v1/expenses/{EXPENSE_ID}",
                     json={"note": "给猫咪买进口猫粮"},
                     headers={"Authorization": f"Bearer {TOKEN_A}"})
    assert resp.status_code == 200
    assert resp.json()["note"] == "给猫咪买进口猫粮"
    print(f"  [OK] 修改支出成功")


def test_statistics_overview():
    resp = httpx.get(f"{BASE}/api/v1/statistics/overview",
                     headers={"Authorization": f"Bearer {TOKEN_A}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["today"] >= 0
    assert data["this_year"] >= 0
    print(f"  [OK] 概览统计: {data}")


def test_statistics_by_category():
    resp = httpx.get(f"{BASE}/api/v1/statistics/by_category",
                     headers={"Authorization": f"Bearer {TOKEN_A}"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) > 0
    print(f"  [OK] 按分类统计: {len(data)} 个分类有数据")


def test_statistics_by_tag():
    resp = httpx.get(f"{BASE}/api/v1/statistics/by_tag",
                     headers={"Authorization": f"Bearer {TOKEN_A}"})
    assert resp.status_code == 200
    print(f"  [OK] 按标签统计: {len(resp.json())} 个标签")


def test_statistics_monthly():
    resp = httpx.get(f"{BASE}/api/v1/statistics/monthly",
                     headers={"Authorization": f"Bearer {TOKEN_A}"})
    assert resp.status_code == 200
    print(f"  [OK] 月度统计: {len(resp.json())} 个月")


def test_user_isolation():
    """用户A的数据不应出现在用户B中"""
    resp = httpx.get(f"{BASE}/api/v1/expenses",
                     headers={"Authorization": f"Bearer {TOKEN_B}"})
    assert resp.status_code == 200
    assert resp.json()["total"] == 0
    print(f"  [OK] 用户隔离: 用户B看不到用户A的数据")


def test_delete_category_blocked():
    """有支出的分类不能删除"""
    resp = httpx.delete(f"{BASE}/api/v1/categories/{CATEGORY_ID}",
                        headers={"Authorization": f"Bearer {TOKEN_A}"})
    assert resp.status_code == 400
    print(f"  [OK] 有支出的分类删除被阻止")


def test_delete_expense():
    resp = httpx.delete(f"{BASE}/api/v1/expenses/{EXPENSE_ID}",
                        headers={"Authorization": f"Bearer {TOKEN_A}"})
    assert resp.status_code == 200
    assert resp.json()["deleted"] is True
    print(f"  [OK] 删除支出成功")


def test_profile():
    resp = httpx.get(f"{BASE}/api/v1/user/profile",
                     headers={"Authorization": f"Bearer {TOKEN_A}"})
    assert resp.status_code == 200
    assert resp.json()["user"]["username"] == "testuser_a"
    print(f"  [OK] 获取个人信息成功")


def test_update_profile():
    resp = httpx.put(f"{BASE}/api/v1/user/profile",
                     json={"nickname": "小明"},
                     headers={"Authorization": f"Bearer {TOKEN_A}"})
    assert resp.status_code == 200
    assert resp.json()["user"]["nickname"] == "小明"
    print(f"  [OK] 修改昵称成功")


if __name__ == "__main__":
    tests = [
        test_register_a, test_register_b, test_register_duplicate,
        test_login, test_login_wrong_password, test_refresh_token,
        test_preset_categories, test_create_category,
        test_create_tag, test_create_tag2,
        test_create_expense, test_list_expenses,
        test_expense_filter_by_tag, test_expense_filter_by_keyword,
        test_update_expense,
        test_statistics_overview, test_statistics_by_category,
        test_statistics_by_tag, test_statistics_monthly,
        test_user_isolation, test_delete_category_blocked,
        test_delete_expense, test_profile, test_update_profile,
    ]

    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"  [FAIL] {test.__name__}: {e}")

    print(f"\n{'='*40}")
    print(f"结果: {passed} 通过, {failed} 失败, 共 {len(tests)} 项")
    print(f"{'='*40}")
