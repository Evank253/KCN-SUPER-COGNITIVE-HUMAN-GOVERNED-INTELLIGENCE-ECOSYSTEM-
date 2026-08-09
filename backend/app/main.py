"""
KCN Super Cognitive Human Governed Intelligence Ecosystem
Backend Application — FastAPI entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.middleware.logging import LoggingMiddleware
from app.routes import (
    auth,
    fable_mythos_tools,
    frontier_tools,
    governance,
    health,
    intelligence,
    memory,
    skills,
    verification,
    vibe,
)

setup_logging()

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
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(LoggingMiddleware)

app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, prefix=settings.api_prefix, tags=["Authentication"])
app.include_router(governance.router, prefix=settings.api_prefix, tags=["Governance"])
app.include_router(intelligence.router, prefix=settings.api_prefix, tags=["Intelligence"])
app.include_router(verification.router, prefix=settings.api_prefix, tags=["Verification"])
app.include_router(vibe.router, prefix=settings.api_prefix, tags=["Vibe · Jarvis · Kronos"])
app.include_router(frontier_tools.router, prefix=settings.api_prefix, tags=["Frontier Tools"])
app.include_router(
    fable_mythos_tools.router, prefix=settings.api_prefix, tags=["Fable · Mythos-style Agent Tools"]
)
app.include_router(memory.router, prefix=settings.api_prefix, tags=["Memory"])
app.include_router(skills.router, prefix=settings.api_prefix, tags=["Skills"])
