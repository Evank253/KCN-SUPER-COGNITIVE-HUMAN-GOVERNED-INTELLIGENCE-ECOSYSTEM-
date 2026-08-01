"""
KCN Super Cognitive Human Governed Intelligence Ecosystem
Backend Application — FastAPI entry point.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.database.session import init_db
from app.middleware.logging import LoggingMiddleware
from app.routes import (
    agents,
    auth,
    governance,
    health,
    intelligence,
    missions,
    users,
    verification,
)
from app.routes import audit as audit_route

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Initialise database tables on startup."""
    await init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    description=(
        "KCN Super Cognitive Human Governed Intelligence Ecosystem API. "
        "A modular platform where humans and intelligent systems collaborate "
        "through governance, verification, security, knowledge management, "
        "education, and innovation."
    ),
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Structured request/response logging middleware
app.add_middleware(LoggingMiddleware)

# Register routers
app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, prefix=settings.api_prefix, tags=["Authentication"])
app.include_router(users.router, prefix=settings.api_prefix, tags=["Users"])
app.include_router(agents.router, prefix=settings.api_prefix, tags=["Agents"])
app.include_router(missions.router, prefix=settings.api_prefix, tags=["Missions"])
app.include_router(audit_route.router, prefix=settings.api_prefix, tags=["Audit Logs"])
app.include_router(
    governance.router, prefix=settings.api_prefix, tags=["Governance"]
)
app.include_router(
    intelligence.router, prefix=settings.api_prefix, tags=["Intelligence"]
)
app.include_router(
    verification.router, prefix=settings.api_prefix, tags=["Verification"]
)
