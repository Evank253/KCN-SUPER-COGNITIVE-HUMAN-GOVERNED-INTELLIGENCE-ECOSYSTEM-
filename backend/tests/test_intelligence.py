"""
Unit tests for intelligence and verification routes.
"""

from fastapi.testclient import TestClient


class TestIntelligenceAnalyze:
    """Tests for POST /api/v1/intelligence/analyze."""

    def test_analyze_returns_200(self, client: TestClient) -> None:
        """Analyze endpoint should return HTTP 200."""
        response = client.post(
            "/api/v1/intelligence/analyze",
            json={"query": "What are best practices for secure coding?"},
        )
        assert response.status_code == 200

    def test_analyze_returns_result_id(self, client: TestClient) -> None:
        """Analyze endpoint should return a result ID."""
        response = client.post(
            "/api/v1/intelligence/analyze",
            json={"query": "Test query"},
        )
        data = response.json()
        assert "id" in data
        assert data["id"].startswith("intel-")

    def test_analyze_status_is_pending_verification(
        self, client: TestClient
    ) -> None:
        """Analysis result should start with pending_verification status."""
        response = client.post(
            "/api/v1/intelligence/analyze",
            json={"query": "Test query"},
        )
        data = response.json()
        assert data["status"] == "pending_verification"

    def test_analyze_with_module_parameter(self, client: TestClient) -> None:
        """Should accept a specific module parameter."""
        response = client.post(
            "/api/v1/intelligence/analyze",
            json={"query": "Test reasoning query", "module": "reasoning"},
        )
        assert response.status_code == 200
        assert response.json()["module"] == "reasoning"

    def test_analyze_with_invalid_module(self, client: TestClient) -> None:
        """Invalid module name should return 422."""
        response = client.post(
            "/api/v1/intelligence/analyze",
            json={"query": "Test query", "module": "nonexistent_module"},
        )
        assert response.status_code == 422

    def test_analyze_with_empty_query(self, client: TestClient) -> None:
        """Empty query should return 422."""
        response = client.post(
            "/api/v1/intelligence/analyze",
            json={"query": ""},
        )
        assert response.status_code == 422


class TestVerificationResults:
    """Tests for GET /api/v1/verification/results/{result_id}."""

    def test_get_verification_result_for_valid_id(
        self, client: TestClient
    ) -> None:
        """Valid intelligence result ID should return a verification result."""
        response = client.get("/api/v1/verification/results/intel-abc123def456")
        assert response.status_code == 200

    def test_get_verification_result_has_confidence_score(
        self, client: TestClient
    ) -> None:
        """Verification result should include a confidence score."""
        response = client.get("/api/v1/verification/results/intel-abc123def456")
        data = response.json()
        assert "confidence_score" in data
        assert 0.0 <= data["confidence_score"] <= 1.0

    def test_get_verification_result_has_checks(
        self, client: TestClient
    ) -> None:
        """Verification result should include a list of checks."""
        response = client.get("/api/v1/verification/results/intel-abc123def456")
        data = response.json()
        assert "checks" in data
        assert isinstance(data["checks"], list)

    def test_get_verification_result_invalid_id_returns_404(
        self, client: TestClient
    ) -> None:
        """Invalid (non-intel) result ID should return 404."""
        response = client.get("/api/v1/verification/results/invalid-id-format")
        assert response.status_code == 404
