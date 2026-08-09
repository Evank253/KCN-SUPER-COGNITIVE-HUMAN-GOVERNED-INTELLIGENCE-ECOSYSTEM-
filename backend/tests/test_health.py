"""
Unit tests for the health and readiness endpoints.
"""

from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Tests for GET /health (liveness)."""

    def test_health_returns_200(self, client: TestClient) -> None:
        """Health endpoint should return HTTP 200."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_healthy_status(self, client: TestClient) -> None:
        """Health endpoint should report status=healthy."""
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "healthy"

    def test_health_returns_version(self, client: TestClient) -> None:
        """Health endpoint should include the application version."""
        response = client.get("/health")
        data = response.json()
        assert "version" in data
        assert isinstance(data["version"], str)

    def test_health_returns_environment(self, client: TestClient) -> None:
        """Health endpoint should include the environment name."""
        response = client.get("/health")
        data = response.json()
        assert "environment" in data
        assert isinstance(data["environment"], str)

    def test_health_returns_timestamp(self, client: TestClient) -> None:
        """Health endpoint should include an ISO-8601 timestamp."""
        response = client.get("/health")
        data = response.json()
        assert "timestamp" in data
        assert "T" in data["timestamp"]  # rough ISO check


class TestReadinessEndpoint:
    """Tests for GET /ready (readiness)."""

    def test_ready_returns_200_when_healthy(self, client: TestClient) -> None:
        """Readiness should return 200 when critical components are up."""
        response = client.get("/ready")
        # Default jwt secret is "change-me-in-production" → degraded but still ready
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"

    def test_ready_includes_components(self, client: TestClient) -> None:
        """Readiness response must list component statuses."""
        response = client.get("/ready")
        data = response.json()
        assert "components" in data
        assert isinstance(data["components"], list)
        names = {c["name"] for c in data["components"]}
        assert "config" in names
        assert "security" in names
        assert "llm_upstream" in names

    def test_ready_config_is_up(self, client: TestClient) -> None:
        """Config component should report up."""
        response = client.get("/ready")
        data = response.json()
        config = next(c for c in data["components"] if c["name"] == "config")
        assert config["status"] == "up"

    def test_ready_security_degraded_on_default_secret(self, client: TestClient) -> None:
        """Default JWT secret should be reported as degraded, not down."""
        response = client.get("/ready")
        data = response.json()
        security = next(c for c in data["components"] if c["name"] == "security")
        assert security["status"] in ("up", "degraded")

    def test_ready_returns_version_and_timestamp(self, client: TestClient) -> None:
        """Readiness payload should include version and timestamp."""
        response = client.get("/ready")
        data = response.json()
        assert "version" in data
        assert "timestamp" in data
