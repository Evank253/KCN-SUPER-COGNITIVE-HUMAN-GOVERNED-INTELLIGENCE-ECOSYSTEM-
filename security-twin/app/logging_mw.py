"""Heavy request logging middleware for the twin — writes to audit store."""

from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.audit_store import record


class TwinAuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        import time

        start = time.perf_counter()
        client = request.client.host if request.client else "unknown"

        headers = {
            k: ("[REDACTED]" if k.lower() in {"authorization", "cookie"} else v)
            for k, v in request.headers.items()
        }

        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)

        record(
            "twin_request",
            method=request.method,
            path=str(request.url.path),
            query=str(request.url.query) if request.url.query else None,
            client=client,
            status=response.status_code,
            duration_ms=duration_ms,
            headers=headers,
            user_agent=request.headers.get("user-agent"),
        )

        response.headers["X-KCN-Twin"] = "true"
        response.headers["X-KCN-Twin-Version"] = "0.2.0"
        response.headers["X-KCN-Twin-Notice"] = "TEST-TARGET-ONLY"
        return response
