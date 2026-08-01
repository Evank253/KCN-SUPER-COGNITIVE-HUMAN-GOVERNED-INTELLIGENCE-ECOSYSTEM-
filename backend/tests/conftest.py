"""
Backend test suite — shared fixtures and configuration.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client() -> TestClient:
    """Return a synchronous test client for the FastAPI application."""
    return TestClient(app)
