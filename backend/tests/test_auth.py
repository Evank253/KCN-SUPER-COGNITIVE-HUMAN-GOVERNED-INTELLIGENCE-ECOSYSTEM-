"""
Unit tests for authentication routes.
"""

from fastapi.testclient import TestClient


class TestAuthRegister:
    """Tests for POST /api/v1/auth/register."""

    def test_register_new_user(self, client: TestClient) -> None:
        """New user registration should return 201 with user data."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "Secure123!",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert "hashed_password" not in data

    def test_register_duplicate_username(self, client: TestClient) -> None:
        """Duplicate username should return 409."""
        payload = {
            "username": "dupuser",
            "email": "dup1@example.com",
            "password": "Secure123!",
        }
        client.post("/api/v1/auth/register", json=payload)
        response = client.post(
            "/api/v1/auth/register",
            json={**payload, "email": "dup2@example.com"},
        )
        assert response.status_code == 409

    def test_register_short_password_fails(self, client: TestClient) -> None:
        """Password shorter than 8 chars should return 422."""
        response = client.post(
            "/api/v1/auth/register",
            json={"username": "badpw", "email": "badpw@example.com", "password": "short"},
        )
        assert response.status_code == 422


class TestAuthLogin:
    """Tests for POST /api/v1/auth/login."""

    def test_login_with_valid_credentials(
        self, client: TestClient, registered_user: dict
    ) -> None:
        """Valid credentials should return tokens."""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "Test1234!"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_with_invalid_password(
        self, client: TestClient, registered_user: dict
    ) -> None:
        """Invalid password should return 401."""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "wrongpassword"},
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
            json={"username": "testuser", "password": ""},
        )
        assert response.status_code == 422


class TestAuthRefresh:
    """Tests for POST /api/v1/auth/refresh."""

    def test_refresh_with_valid_token(
        self, client: TestClient, registered_user: dict
    ) -> None:
        """Valid refresh token should return a new access token."""
        login_resp = client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "Test1234!"},
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
