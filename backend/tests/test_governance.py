"""Tests for governance policy and human approval workflows."""

from fastapi.testclient import TestClient


class TestGovernancePolicies:
    def test_list_policies_returns_200(self, client: TestClient) -> None:
        response = client.get("/api/v1/governance/policies")
        assert response.status_code == 200

    def test_list_policies_returns_list(self, client: TestClient) -> None:
        data = client.get("/api/v1/governance/policies").json()
        assert isinstance(data["policies"], list)

    def test_list_policies_total_matches(self, client: TestClient) -> None:
        data = client.get("/api/v1/governance/policies").json()
        assert data["total"] == len(data["policies"])

    def test_policies_have_required_fields(self, client: TestClient) -> None:
        policies = client.get("/api/v1/governance/policies").json()["policies"]
        for policy in policies:
            assert {"id", "name", "enabled"}.issubset(policy)


class TestGovernanceApprovals:
    def _submit(self, client: TestClient, case_id: str | None = None) -> dict:
        payload = {
            "action_type": "high_risk_operation",
            "description": "Test approval request",
        }
        if case_id:
            payload["case_id"] = case_id
        response = client.post("/api/v1/governance/approvals", json=payload)
        assert response.status_code == 201
        return response.json()

    def test_submit_approval_returns_201(self, client: TestClient) -> None:
        data = self._submit(client, "case-test-1")
        assert data["status"] == "pending"
        assert data["case_id"] == "case-test-1"

    def test_submit_approval_persists_and_can_be_retrieved(self, client: TestClient) -> None:
        data = self._submit(client, "case-test-2")
        response = client.get(f"/api/v1/governance/approvals/{data['id']}")
        assert response.status_code == 200
        assert response.json()["status"] == "pending"
        assert response.json()["case_id"] == "case-test-2"

    def test_approval_requires_human_decision_for_transition(self, client: TestClient) -> None:
        data = self._submit(client, "case-test-3")
        response = client.post(
            f"/api/v1/governance/approvals/{data['id']}/decision",
            json={"status": "approved", "human_authority": "human-test"},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "approved"
        assert response.json()["human_authority"] == "human-test"

    def test_approval_cannot_be_decided_twice(self, client: TestClient) -> None:
        data = self._submit(client, "case-test-4")
        path = f"/api/v1/governance/approvals/{data['id']}/decision"
        assert client.post(path, json={"status": "rejected", "human_authority": "human-test"}).status_code == 200
        assert client.post(path, json={"status": "approved", "human_authority": "human-test"}).status_code == 409

    def test_missing_action_type_is_rejected(self, client: TestClient) -> None:
        response = client.post("/api/v1/governance/approvals", json={"description": "Missing action_type"})
        assert response.status_code == 422
