"""
Unit tests for governance routes.
"""

from fastapi.testclient import TestClient


class TestGovernancePolicies:
    """Tests for GET /api/v1/governance/policies."""

    def test_list_policies_returns_200(self, client: TestClient) -> None:
        """Policies endpoint should return HTTP 200."""
        response = client.get("/api/v1/governance/policies")
        assert response.status_code == 200

    def test_list_policies_returns_list(self, client: TestClient) -> None:
        """Policies endpoint should return a list of policies."""
        response = client.get("/api/v1/governance/policies")
        data = response.json()
        assert "policies" in data
        assert isinstance(data["policies"], list)

    def test_list_policies_total_matches(self, client: TestClient) -> None:
        """Total count should match the number of returned policies."""
        response = client.get("/api/v1/governance/policies")
        data = response.json()
        assert data["total"] == len(data["policies"])

    def test_policies_have_required_fields(self, client: TestClient) -> None:
        """Each policy should have required fields."""
        response = client.get("/api/v1/governance/policies")
        policies = response.json()["policies"]
        for policy in policies:
            assert "id" in policy
            assert "name" in policy
            assert "enabled" in policy


class TestGovernanceApprovals:
    """Tests for POST /api/v1/governance/approvals."""

    def test_submit_approval_returns_201(self, client: TestClient) -> None:
        """Approval submission should return HTTP 201."""
        response = client.post(
            "/api/v1/governance/approvals",
            json={
                "action_type": "high_risk_operation",
                "description": "Test approval request",
            },
        )
        assert response.status_code == 201

    def test_submit_approval_returns_pending_status(
        self, client: TestClient
    ) -> None:
        """Submitted approval should have pending status."""
        response = client.post(
            "/api/v1/governance/approvals",
            json={
                "action_type": "test_action",
                "description": "Test description",
            },
        )
        data = response.json()
        assert data["status"] == "pending"

    def test_submit_approval_requires_action_type(
        self, client: TestClient
    ) -> None:
        """Missing action_type should return 422."""
        response = client.post(
            "/api/v1/governance/approvals",
            json={"description": "Missing action_type"},
        )
        assert response.status_code == 422
