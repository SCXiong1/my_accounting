"""PIN authentication integration tests.

Requires running server:
  APP_DATABASE_PATH=./data/test.db uvicorn main:app --host 0.0.0.0 --port 8080
  pytest test_pin_auth.py -v
"""

import httpx
import pytest

pytest_plugins = ["conftest_integration"]


class _S:
    session: httpx.Cookies | None = None


@pytest.fixture(scope="module")
def S():
    return _S()


def test_login_with_default_pin(S: _S):
    resp = httpx.post(f"{BASE}/api/auth/login", json={
        "username": "user1",
        "pin": "1234",
    })
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    data = resp.json()
    assert data["user"]["username"] == "user1"
    assert data["must_change_pin"] is True
    S.session = resp.cookies
    print("  [OK] Login with default PIN")


def test_login_with_wrong_pin(S: _S):
    resp = httpx.post(f"{BASE}/api/auth/login", json={
        "username": "user1",
        "pin": "9999",
    })
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}"
    print("  [OK] Login with wrong PIN rejected")


def test_get_security_question():
    resp = httpx.get(f"{BASE}/api/auth/security-question")
    assert resp.status_code == 200
    data = resp.json()
    assert data["question"] == "小1是谁？"
    print("  [OK] Get security question")


def test_verify_security_answer():
    resp = httpx.post(f"{BASE}/api/auth/verify-security", json={
        "username": "user1",
        "answer": "小1",
    })
    assert resp.status_code == 200
    print("  [OK] Verify security answer")


def test_verify_security_answer_wrong():
    resp = httpx.post(f"{BASE}/api/auth/verify-security", json={
        "username": "user1",
        "answer": "wrong",
    })
    assert resp.status_code == 400
    print("  [OK] Wrong security answer rejected")


def test_reset_pin_via_security():
    resp = httpx.post(f"{BASE}/api/auth/reset-pin", json={
        "username": "user1",
        "answer": "小1",
        "new_pin": "5678",
    })
    assert resp.status_code == 200
    print("  [OK] Reset PIN via security question")

    # Login with new PIN
    resp = httpx.post(f"{BASE}/api/auth/login", json={
        "username": "user1",
        "pin": "5678",
    })
    assert resp.status_code == 200
    assert resp.json()["must_change_pin"] is False
    print("  [OK] Login with new PIN")


def test_change_pin(S: _S):
    resp = httpx.post(
        f"{BASE}/api/auth/change-pin",
        json={
            "current_pin": "5678",
            "new_pin": "1234",
        },
        cookies=S.session,
    )
    assert resp.status_code == 200
    print("  [OK] Change PIN")

    # Login with changed PIN
    resp = httpx.post(f"{BASE}/api/auth/login", json={
        "username": "user1",
        "pin": "1234",
    })
    assert resp.status_code == 200
    S.session = resp.cookies
    print("  [OK] Login with changed PIN")


def test_change_pin_wrong_current(S: _S):
    resp = httpx.post(
        f"{BASE}/api/auth/change-pin",
        json={
            "current_pin": "9999",
            "new_pin": "5678",
        },
        cookies=S.session,
    )
    assert resp.status_code == 400
    print("  [OK] Change PIN with wrong current rejected")


def test_profile_returns_pin_changed(S: _S):
    resp = httpx.get(f"{BASE}/api/v1/user/profile", cookies=S.session)
    assert resp.status_code == 200
    data = resp.json()
    assert data["user"]["pin_changed"] is True
    print("  [OK] Profile returns pin_changed")


def test_protected_endpoint_without_session():
    resp = httpx.get(f"{BASE}/api/v1/user/profile")
    assert resp.status_code == 401
    print("  [OK] Protected endpoint without session returns 401")


def test_logout(S: _S):
    resp = httpx.post(f"{BASE}/api/auth/logout", cookies=S.session)
    assert resp.status_code == 200

    # Verify session is cleared
    resp = httpx.get(f"{BASE}/api/v1/user/profile", cookies=S.session)
    assert resp.status_code == 401
    print("  [OK] Logout clears session")
