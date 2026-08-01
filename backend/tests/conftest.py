"""
Backend test suite — shared fixtures and configuration.

Uses an in-memory SQLite database so tests never touch production data.
"""

from collections.abc import AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# ── Test database ──────────────────────────────────────────────────────────
# Use a shared in-memory SQLite so all connections see the same data.
_TEST_DB_URL = "sqlite+aiosqlite:///file:testdb?mode=memory&cache=shared&uri=true"
_test_engine = create_async_engine(_TEST_DB_URL, echo=False)
_TestSession = async_sessionmaker(_test_engine, expire_on_commit=False, class_=AsyncSession)


async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with _TestSession() as session:
        yield session


# Patch the module-level engine BEFORE the app lifespan uses it.
import app.database.session as _db_session

_db_session.engine = _test_engine
_db_session.AsyncSessionLocal = _TestSession

from app.database.session import get_db
from app.main import app

# ── Fixtures ───────────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def client() -> TestClient:  # type: ignore[override]
    """
    Return a synchronous TestClient backed by an in-memory SQLite database.

    The lifespan runs once per session and creates all tables via init_db().
    """
    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def registered_user(client: TestClient) -> dict:
    """Register a test user and return the parsed response body."""
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "Test1234!",
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


@pytest.fixture(scope="session")
def auth_headers(client: TestClient, registered_user: dict) -> dict:
    """Return Authorization headers for the registered test user."""
    resp = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "Test1234!"},
    )
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": "Bearer " + token}
