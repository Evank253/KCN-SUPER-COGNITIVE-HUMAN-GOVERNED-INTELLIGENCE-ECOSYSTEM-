"""
Unit tests for authentication routes.
"""

from fastapi.testclient import TestClient


class TestAuthLogin:
    """Tests for POST /api/v1/auth/login."""

    def test_login_with_valid_credentials(self, client: TestClient) -> None:
        """Valid credentials should return tokens."""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "changeme"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_with_invalid_password(self, client: TestClient) -> None:
        """Invalid password should return 401."""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "wrongpassword"},
        )
        assert response.status_code == 401

    def test_login_with_unknown_user(self, client: TestClient) -> None:
        """Unknown username should return 401."""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "unknown", "password": "changeme"},
        )
        assert response.status_code == 401

    def test_login_with_empty_password(self, client: TestClient) -> None:
        """Empty password should return 422 validation error."""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": ""},
        )
        assert response.status_code == 422


class TestAuthRefresh:
    """Tests for POST /api/v1/auth/refresh."""

    def test_refresh_with_valid_token(self, client: TestClient) -> None:
        """Valid refresh token should return a new access token."""
        login_resp = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "changeme"},
        )
        refresh_token = login_resp.json()["refresh_token"]

        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    def test_refresh_with_invalid_token(self, client: TestClient) -> None:
        """Invalid refresh token should return 401."""
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "this-is-not-a-valid-token"},
        )
        assert response.status_code == 401


class TestAuthLogout:
    """Tests for POST /api/v1/auth/logout."""

    def test_logout_returns_200(self, client: TestClient) -> None:
        """Logout should return HTTP 200."""
        response = client.post("/api/v1/auth/logout")
        assert response.status_code == 200

    def test_logout_returns_message(self, client: TestClient) -> None:
        """Logout should return a success message."""
        response = client.post("/api/v1/auth/logout")
        data = response.json()
        assert "message" in data
