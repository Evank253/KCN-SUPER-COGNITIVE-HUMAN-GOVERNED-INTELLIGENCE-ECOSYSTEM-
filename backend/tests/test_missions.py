"""
Unit tests for mission routes.
"""

from fastapi.testclient import TestClient


class TestCreateMission:
    """Tests for POST /api/v1/missions/create."""

    def test_create_mission_requires_auth(self, client: TestClient) -> None:
        response = client.post(
            "/api/v1/missions/create",
            json={"title": "Test", "description": "desc"},
        )
        assert response.status_code in (401, 403)

    def test_create_mission_success(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        """Mission creation should return 201 with mission data."""
        response = client.post(
            "/api/v1/missions/create",
            json={
                "title": "Analyze market trends",
                "description": "Research Q4 market data and produce a report.",
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Analyze market trends"
        assert data["status"] == "pending"
        assert "id" in data

    def test_create_mission_invalid_agent(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        """Mission with unknown agent_id should return 404."""
        response = client.post(
            "/api/v1/missions/create",
            json={
                "title": "Test",
                "description": "desc",
                "agent_id": "00000000-0000-0000-0000-000000000000",
            },
            headers=auth_headers,
        )
        assert response.status_code == 404


class TestListMissions:
    """Tests for GET /api/v1/missions."""

    def test_list_missions_requires_auth(self, client: TestClient) -> None:
        response = client.get("/api/v1/missions")
        assert response.status_code in (401, 403)

    def test_list_missions_returns_list(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        response = client.get("/api/v1/missions", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestGetMission:
    """Tests for GET /api/v1/missions/{id}."""

    def test_get_mission_not_found(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        response = client.get(
            "/api/v1/missions/00000000-0000-0000-0000-000000000000",
            headers=auth_headers,
        )
        assert response.status_code == 404

    def test_get_mission_success(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        create_resp = client.post(
            "/api/v1/missions/create",
            json={"title": "Get Test", "description": "desc"},
            headers=auth_headers,
        )
        mission_id = create_resp.json()["id"]
        response = client.get(
            f"/api/v1/missions/{mission_id}", headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["id"] == mission_id
