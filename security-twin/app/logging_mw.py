"""Heavy request logging middleware for the twin."""

import json
import logging
import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("kcn.twin.audit")


class TwinAuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start = time.perf_counter()
        client = request.client.host if request.client else "unknown"

        # Redact sensitive headers
        headers = {
            k: ("[REDACTED]" if k.lower() in {"authorization", "cookie"} else v)
            for k, v in request.headers.items()
        }

        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)

        event = {
            "event": "twin_request",
            "method": request.method,
            "path": str(request.url.path),
            "query": str(request.url.query) if request.url.query else None,
            "client": client,
            "status": response.status_code,
            "duration_ms": duration_ms,
            "headers": headers,
            "twin": True,
        }
        logger.info(json.dumps(event))

        response.headers["X-KCN-Twin"] = "true"
        response.headers["X-KCN-Twin-Version"] = "0.1.0"
        return response
