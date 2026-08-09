"""
Health and readiness endpoints.
No authentication required — used by load balancers, orchestrators, and CI.
"""

from datetime import datetime, timezone
from typing import Literal

import httpx
from fastapi import APIRouter, Response, status
from pydantic import BaseModel, Field

from app.core.config import settings

router = APIRouter()


class ComponentStatus(BaseModel):
    """Status of a single dependency or subsystem."""

    name: str
    status: Literal["up", "down", "degraded"]
    detail: str | None = None


class HealthResponse(BaseModel):
    """Liveness probe response."""

    status: Literal["healthy", "unhealthy"] = "healthy"
    version: str
    environment: str
    timestamp: str


class ReadinessResponse(BaseModel):
    """Readiness probe response — indicates whether the service can accept traffic."""

    status: Literal["ready", "not_ready"]
    version: str
    timestamp: str
    components: list[ComponentStatus] = Field(default_factory=list)


def _check_config() -> ComponentStatus:
    """Verify application settings loaded successfully."""
    try:
        _ = settings.app_name
        _ = settings.app_version
        return ComponentStatus(name="config", status="up", detail="settings loaded")
    except Exception as exc:  # noqa: BLE001 — pragma: no cover - readiness probe must never raise
        return ComponentStatus(name="config", status="down", detail=str(exc))


def _check_security() -> ComponentStatus:
    """Verify JWT configuration is usable."""
    if not settings.jwt_secret_key:
        return ComponentStatus(
            name="security",
            status="down",
            detail="jwt_secret_key is empty",
        )
    if settings.jwt_secret_key == "change-me-in-production":
        # Still functional in development, but flag as degraded
        return ComponentStatus(
            name="security",
            status="degraded",
            detail="using default jwt_secret_key — change before production",
        )
    return ComponentStatus(name="security", status="up", detail="jwt secret configured")


async def _check_llm_upstream() -> ComponentStatus:
    """Optionally probe the configured LLM base URL (OpenAI-compatible)."""
    base = (settings.kcn_llm_base_url or "").rstrip("/")
    if not base:
        return ComponentStatus(
            name="llm_upstream",
            status="up",
            detail="not configured (optional)",
        )

    # Lightweight reachability check — most providers expose /models or just accept HEAD
    url = f"{base}/models"
    headers: dict[str, str] = {}
    if settings.kcn_llm_api_key:
        headers["Authorization"] = f"Bearer {settings.kcn_llm_api_key}"

    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code < 500:
                return ComponentStatus(
                    name="llm_upstream",
                    status="up",
                    detail=f"reachable ({resp.status_code})",
                )
            return ComponentStatus(
                name="llm_upstream",
                status="degraded",
                detail=f"upstream returned {resp.status_code}",
            )
    except httpx.TimeoutException:
        return ComponentStatus(
            name="llm_upstream",
            status="degraded",
            detail="timeout contacting upstream",
        )
    except Exception as exc:  # noqa: BLE001 — readiness probe must never raise
        return ComponentStatus(
            name="llm_upstream",
            status="degraded",
            detail=f"unreachable: {exc}",
        )


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Liveness probe",
    status_code=status.HTTP_200_OK,
)
async def health_check() -> HealthResponse:
    """
    Basic liveness check.

    Always returns 200 if the process is running and can serve requests.
    Suitable for Kubernetes livenessProbe / load-balancer health checks.
    """
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        environment=settings.app_env,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    summary="Readiness probe",
    responses={
        200: {"description": "Service is ready to accept traffic"},
        503: {"description": "Service is not ready (one or more critical components down)"},
    },
)
async def readiness_check(response: Response) -> ReadinessResponse:
    """
    Readiness check — verifies the service can safely accept traffic.

    Critical components (config, security) must be "up".
    Optional components (llm_upstream) may be degraded without failing readiness.
    Returns HTTP 503 when any critical component is down.
    """
    components: list[ComponentStatus] = [
        _check_config(),
        _check_security(),
        await _check_llm_upstream(),
    ]

    critical_names = {"config", "security"}
    critical_down = any(
        c.name in critical_names and c.status == "down" for c in components
    )

    overall: Literal["ready", "not_ready"] = "not_ready" if critical_down else "ready"

    if overall == "not_ready":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return ReadinessResponse(
        status=overall,
        version=settings.app_version,
        timestamp=datetime.now(timezone.utc).isoformat(),
        components=components,
    )
