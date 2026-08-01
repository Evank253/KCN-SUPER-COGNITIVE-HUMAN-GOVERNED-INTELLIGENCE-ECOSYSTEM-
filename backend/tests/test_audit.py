"""
Unit tests for audit log routes.
"""

from fastapi.testclient import TestClient


class TestListAuditLogs:
    """Tests for GET /api/v1/audit-logs."""

    def test_audit_logs_requires_auth(self, client: TestClient) -> None:
        response = client.get("/api/v1/audit-logs")
        assert response.status_code in (401, 403)

    def test_audit_logs_returns_list(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        """Authenticated user should receive a list of audit entries."""
        response = client.get("/api/v1/audit-logs", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_audit_logs_have_required_fields(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        """Each audit entry should contain expected fields."""
        response = client.get("/api/v1/audit-logs", headers=auth_headers)
        entries = response.json()
        assert len(entries) > 0  # at least register/login were audited
        for entry in entries:
            assert "id" in entry
            assert "action" in entry
            assert "timestamp" in entry
