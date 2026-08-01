"""
Unit tests for user routes.
"""

from fastapi.testclient import TestClient


class TestGetMe:
    """Tests for GET /api/v1/users/me."""

    def test_get_me_requires_auth(self, client: TestClient) -> None:
        """Unauthenticated request should return 403 (missing bearer)."""
        response = client.get("/api/v1/users/me")
        assert response.status_code in (401, 403)

    def test_get_me_returns_current_user(
        self, client: TestClient, registered_user: dict, auth_headers: dict
    ) -> None:
        """Authenticated request should return current user data."""
        response = client.get("/api/v1/users/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "testuser@example.com"
        assert "hashed_password" not in data


class TestUpdateProfile:
    """Tests for PUT /api/v1/users/profile."""

    def test_update_profile_requires_auth(self, client: TestClient) -> None:
        """Unauthenticated request should return 401 or 403."""
        response = client.put(
            "/api/v1/users/profile", json={"display_name": "Test"}
        )
        assert response.status_code in (401, 403)

    def test_update_profile_display_name(
        self, client: TestClient, registered_user: dict, auth_headers: dict
    ) -> None:
        """Should update and return the new display name."""
        response = client.put(
            "/api/v1/users/profile",
            json={"display_name": "My Display Name"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["profile"]["display_name"] == "My Display Name"

    def test_update_profile_no_fields_fails(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        """Empty update body should return 422."""
        response = client.put(
            "/api/v1/users/profile", json={}, headers=auth_headers
        )
        assert response.status_code == 422
