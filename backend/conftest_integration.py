"""Integration test shared fixtures and helpers.

Provides:
- Environment variable setup for test database isolation
- BASE URL constant
- _auth() helper for Authorization header
- _S state class template for module-level shared state
- S fixture for dependency injection
"""

import os

import pytest

# Test database isolation — must be set before server starts
os.environ.setdefault("APP_DATABASE_PATH", "./data/test.db")

BASE = os.environ.get("TEST_BASE", "http://localhost:8080")


def _auth(token: str | None) -> dict:
    """Return Authorization header dict."""
    return {"Authorization": f"Bearer {token}"}


class _S:
    """Module-level shared state base class.
    
    Subclass this in each test module to add module-specific fields.
    """
    pass


@pytest.fixture(scope="module")
def S():
    """Provide module-level shared state instance."""
    return _S()
