"""
Unit tests for agent routes.
"""

from fastapi.testclient import TestClient


class TestCreateAgent:
    """Tests for POST /api/v1/agents/create."""

    def test_create_agent_requires_auth(self, client: TestClient) -> None:
        response = client.post(
            "/api/v1/agents/create",
            json={"name": "Test Agent"},
        )
        assert response.status_code in (401, 403)

    def test_create_agent_success(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        """Agent creation should return 201 with agent data."""
        response = client.post(
            "/api/v1/agents/create",
            json={
                "name": "Research-Agent-001",
                "agent_type": "research",
                "description": "Performs research tasks",
                "permissions": ["read_documents", "analyze_data"],
                "configuration": {},
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Research-Agent-001"
        assert data["agent_type"] == "research"
        assert data["status"] == "inactive"
        assert "id" in data

    def test_create_agent_minimal(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        """Agent creation with only required fields should succeed."""
        response = client.post(
            "/api/v1/agents/create",
            json={"name": "Minimal Agent"},
            headers=auth_headers,
        )
        assert response.status_code == 201


class TestListAgents:
    """Tests for GET /api/v1/agents."""

    def test_list_agents_requires_auth(self, client: TestClient) -> None:
        response = client.get("/api/v1/agents")
        assert response.status_code in (401, 403)

    def test_list_agents_returns_list(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        """Should return a list of agents owned by the current user."""
        response = client.get("/api/v1/agents", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestGetAgent:
    """Tests for GET /api/v1/agents/{id}."""

    def test_get_agent_not_found(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        """Non-existent agent ID should return 404."""
        response = client.get(
            "/api/v1/agents/00000000-0000-0000-0000-000000000000",
            headers=auth_headers,
        )
        assert response.status_code == 404

    def test_get_agent_success(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        """Should return the created agent."""
        create_resp = client.post(
            "/api/v1/agents/create",
            json={"name": "Get Test Agent"},
            headers=auth_headers,
        )
        agent_id = create_resp.json()["id"]
        response = client.get(f"/api/v1/agents/{agent_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["id"] == agent_id


class TestUpdateAgent:
    """Tests for PUT /api/v1/agents/{id}."""

    def test_update_agent_status(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        """Should update and return the modified agent."""
        create_resp = client.post(
            "/api/v1/agents/create",
            json={"name": "Update Test Agent"},
            headers=auth_headers,
        )
        agent_id = create_resp.json()["id"]

        response = client.put(
            f"/api/v1/agents/{agent_id}",
            json={"status": "active"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["status"] == "active"


class TestDeleteAgent:
    """Tests for DELETE /api/v1/agents/{id}."""

    def test_delete_agent_success(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        """Should delete the agent and return 204."""
        create_resp = client.post(
            "/api/v1/agents/create",
            json={"name": "Delete Test Agent"},
            headers=auth_headers,
        )
        agent_id = create_resp.json()["id"]

        response = client.delete(f"/api/v1/agents/{agent_id}", headers=auth_headers)
        assert response.status_code == 204

        # Confirm deletion
        get_resp = client.get(f"/api/v1/agents/{agent_id}", headers=auth_headers)
        assert get_resp.status_code == 404
