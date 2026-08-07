"""
KCN Security Twin — isolated FastAPI target for authorized external testing.

This is NOT the real system. It contains no production secrets or data.
All audit records are marked TWIN TEST LOG — NOT PRODUCTION.
"""

import logging
from typing import Any

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from app.audit_store import get_events, record, summary
from app.config import settings
from app.logging_mw import TwinAuditMiddleware
from app.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger("kcn.twin")

app = FastAPI(
    title="KCN Security Twin",
    description=(
        "ISOLATED TEST TARGET. Disposable twin of the KCN security surface. "
        "No real secrets. No production data. Authorized testing only. "
        "All logs are marked TWIN TEST LOG — NOT PRODUCTION."
    ),
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(TwinAuditMiddleware)

bearer = HTTPBearer(auto_error=False)

# ---------------------------------------------------------------------------
# Stub users (test only)
# ---------------------------------------------------------------------------

from passlib.context import CryptContext

_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

_STUB_USERS = {
    "twin-admin": {
        "username": "twin-admin",
        "hashed_password": _ctx.hash("twin-pass-change-me"),
        "roles": ["admin"],
    },
    "twin-user": {
        "username": "twin-user",
        "hashed_password": _ctx.hash("twin-user-pass"),
        "roles": ["user"],
    },
}


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=128)
    password: str = Field(..., min_length=1, max_length=256)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    twin: bool = True
    notice: str = "KCN SECURITY TWIN — TEST TARGET ONLY"


class RefreshRequest(BaseModel):
    refresh_token: str


class MessageResponse(BaseModel):
    message: str
    twin: bool = True


class RememberRequest(BaseModel):
    content: str
    tags: list[str] = []


class SkillRegisterRequest(BaseModel):
    name: str
    description: str = ""
    version: str = "0.1.0"


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> dict[str, Any]:
    if not creds:
        raise HTTPException(status_code=401, detail="Not authenticated (twin)")
    payload = decode_token(creds.credentials)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid or expired token (twin)")
    return payload


def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if "admin" not in user.get("roles", []):
        raise HTTPException(status_code=403, detail="Admin role required (twin)")
    return user


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.on_event("startup")
async def on_startup():
    record("session_start", service=settings.app_name, version=settings.app_version)
    logger.info("KCN Security Twin started — audit logging active")


@app.get("/")
async def root():
    return {
        "service": "KCN Security Twin",
        "status": "ISOLATED_TEST_TARGET",
        "notice": "This is a disposable twin. No real secrets or production data.",
        "docs": "/docs",
        "audit_export": "/api/v1/audit/export (admin token required)",
        "twin": True,
    }


@app.get("/health")
async def health():
    return {"status": "ok", "twin": True, "service": settings.app_name}


@app.post(f"{settings.api_prefix}/auth/login", response_model=TokenResponse)
async def login(body: LoginRequest):
    user = _STUB_USERS.get(body.username)
    if not user or not verify_password(body.password, user["hashed_password"]):
        record("auth_failure", username=body.username, reason="invalid_credentials")
        logger.warning("Twin login failed for username=%s", body.username)
        raise HTTPException(status_code=401, detail="Invalid credentials (twin)")

    access = create_access_token(user["username"], {"roles": user["roles"]})
    refresh = create_refresh_token(user["username"])
    record("auth_success", username=user["username"], roles=user["roles"])
    logger.info("Twin user authenticated: %s", user["username"])
    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        expires_in=settings.jwt_access_token_expire_minutes * 60,
    )


@app.post(f"{settings.api_prefix}/auth/refresh")
async def refresh(body: RefreshRequest):
    payload = decode_token(body.refresh_token)
    if not payload or payload.get("type") != "refresh":
        record("auth_failure", reason="invalid_refresh_token")
        raise HTTPException(status_code=401, detail="Invalid refresh token (twin)")
    username = payload.get("sub", "")
    user = _STUB_USERS.get(username)
    if not user:
        record("auth_failure", username=username, reason="user_not_found")
        raise HTTPException(status_code=401, detail="User not found (twin)")
    access = create_access_token(username, {"roles": user["roles"]})
    record("auth_refresh", username=username)
    return {
        "access_token": access,
        "token_type": "bearer",
        "expires_in": settings.jwt_access_token_expire_minutes * 60,
        "twin": True,
    }


@app.post(f"{settings.api_prefix}/auth/logout", response_model=MessageResponse)
async def logout():
    record("auth_logout")
    return MessageResponse(message="Logged out (twin — no token blacklist in this target)")


@app.get(f"{settings.api_prefix}/governance/status")
async def governance_status(user: dict = Depends(get_current_user)):
    return {
        "governance": "active",
        "human_approval_required": True,
        "user": user.get("sub"),
        "roles": user.get("roles", []),
        "twin": True,
        "notice": "KCN SECURITY TWIN — TEST TARGET ONLY",
    }


@app.post(f"{settings.api_prefix}/governance/request-approval")
async def request_approval(
    action: str = "generic_action",
    user: dict = Depends(get_current_user),
):
    record("governance_request", action=action, user=user.get("sub"))
    return {
        "request_id": "twin-req-001",
        "action": action,
        "status": "pending_human_approval",
        "requested_by": user.get("sub"),
        "twin": True,
    }


_memory_store: list[dict] = []
_skills_store: dict[str, dict] = {
    "structured_reasoning": {
        "name": "structured_reasoning",
        "version": "0.1.0",
        "status": "active",
    },
    "human_approval": {
        "name": "human_approval",
        "version": "0.1.0",
        "status": "active",
    },
}


@app.post(f"{settings.api_prefix}/memory/remember")
async def remember(body: RememberRequest, user: dict = Depends(get_current_user)):
    entry = {
        "id": f"mem-{len(_memory_store)+1}",
        "content": body.content,
        "tags": body.tags,
        "owner": user.get("sub"),
        "verified": False,
        "twin": True,
    }
    _memory_store.append(entry)
    record("memory_write", owner=user.get("sub"), entry_id=entry["id"])
    return {"status": "stored", "entry": entry, "twin": True}


@app.get(f"{settings.api_prefix}/memory/recall")
async def recall(q: str = "", user: dict = Depends(get_current_user)):
    results = [m for m in _memory_store if q.lower() in m["content"].lower()]
    record("memory_recall", query=q, result_count=len(results), user=user.get("sub"))
    return {"query": q, "results": results[:10], "twin": True}


@app.get(f"{settings.api_prefix}/skills")
async def list_skills(user: dict = Depends(get_current_user)):
    return {"skills": list(_skills_store.values()), "twin": True}


@app.post(f"{settings.api_prefix}/skills/register")
async def register_skill(
    body: SkillRegisterRequest, user: dict = Depends(require_admin)
):
    _skills_store[body.name] = {
        "name": body.name,
        "description": body.description,
        "version": body.version,
        "status": "active",
        "registered_by": user.get("sub"),
        "twin": True,
    }
    record("skill_register", skill=body.name, by=user.get("sub"))
    return {"status": "registered", "skill": _skills_store[body.name], "twin": True}


@app.get(f"{settings.api_prefix}/canary")
async def canary():
    record("canary_hit")
    logger.warning("Canary endpoint hit")
    return {
        "canary": "alive",
        "message": "If you see this, the twin is reachable and logging the hit.",
        "twin": True,
    }


# ---------------------------------------------------------------------------
# Audit export (proof-of-test logs)
# ---------------------------------------------------------------------------


@app.get(f"{settings.api_prefix}/audit/summary")
async def audit_summary(user: dict = Depends(require_admin)):
    """High-level counts for the current twin test session."""
    return summary()


@app.get(f"{settings.api_prefix}/audit/export")
async def audit_export(
    limit: int = 5000,
    format: str = "json",
    user: dict = Depends(require_admin),
):
    """
    Export the twin audit log for the current session.

    Every record is marked TWIN TEST LOG — NOT PRODUCTION.
    This is evidence of activity against the twin only.
    """
    events = get_events(limit=min(limit, 20_000))
    record("audit_export", by=user.get("sub"), count=len(events), format=format)

    if format == "jsonl":
        body = "\n".join(
            __import__("json").dumps(e, default=str) for e in events
        ) + ("\n" if events else "")
        return PlainTextResponse(
            content=body,
            media_type="application/x-ndjson",
            headers={
                "Content-Disposition": "attachment; filename=kcn-twin-audit.jsonl",
                "X-KCN-Twin-Notice": "TWIN-TEST-LOG-NOT-PRODUCTION",
            },
        )

    return JSONResponse(
        content={
            "notice": "TWIN TEST LOG — NOT PRODUCTION",
            "service": "KCN Security Twin",
            "exported_by": user.get("sub"),
            "event_count": len(events),
            "events": events,
        },
        headers={"X-KCN-Twin-Notice": "TWIN-TEST-LOG-NOT-PRODUCTION"},
    )
