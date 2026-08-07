"""
KCN Security Twin — isolated FastAPI target for authorized external testing.

v0.2: rate-limit/lockout, token blacklist, stricter JWT, request size limits.
This is NOT the real system. All audit records are TWIN TEST LOG — NOT PRODUCTION.
"""

import logging
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from app.audit_store import get_events, record, summary
from app.config import settings
from app.logging_mw import TwinAuditMiddleware
from app.rate_limit import is_locked, record_failure, record_success
from app.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.token_blacklist import revoke

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger("kcn.twin")

app = FastAPI(
    title="KCN Security Twin",
    description=(
        "ISOLATED TEST TARGET v0.2. Rate-limited login, token blacklist on logout, "
        "strict JWT claims, request size limits. No real secrets. Authorized testing only."
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
    content: str = Field(..., min_length=1, max_length=settings.memory_max_content_chars)
    tags: list[str] = Field(default_factory=list, max_length=settings.memory_max_tags)


class SkillRegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    description: str = Field(default="", max_length=512)
    version: str = Field(default="0.1.0", max_length=32)


def _client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> dict[str, Any]:
    if not creds:
        raise HTTPException(status_code=401, detail="Not authenticated (twin)")
    payload = decode_token(creds.credentials, expected_type="access", check_blacklist=True)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid, expired, or revoked token (twin)")
    return payload


def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if "admin" not in user.get("roles", []):
        raise HTTPException(status_code=403, detail="Admin role required (twin)")
    return user


@app.middleware("http")
async def body_size_limit(request: Request, call_next):
    cl = request.headers.get("content-length")
    if cl and cl.isdigit() and int(cl) > settings.max_request_body_bytes:
        record(
            "size_reject",
            path=str(request.url.path),
            content_length=int(cl),
            limit=settings.max_request_body_bytes,
        )
        return JSONResponse(
            status_code=413,
            content={
                "detail": "Request body too large (twin)",
                "limit_bytes": settings.max_request_body_bytes,
                "twin": True,
            },
            headers={"X-KCN-Twin": "true"},
        )
    return await call_next(request)


@app.on_event("startup")
async def on_startup():
    record("session_start", service=settings.app_name, version=settings.app_version)
    logger.info("KCN Security Twin v%s started — hardened controls active", settings.app_version)


@app.get("/")
async def root():
    return {
        "service": "KCN Security Twin",
        "version": settings.app_version,
        "status": "ISOLATED_TEST_TARGET",
        "controls": [
            "login_rate_limit_lockout",
            "token_blacklist_on_logout",
            "strict_jwt_claims",
            "request_size_limits",
        ],
        "notice": "Disposable twin. No real secrets or production data.",
        "docs": "/docs",
        "twin": True,
    }


@app.get("/health")
async def health():
    return {"status": "ok", "twin": True, "service": settings.app_name, "version": settings.app_version}


@app.post(f"{settings.api_prefix}/auth/login", response_model=TokenResponse)
async def login(body: LoginRequest, request: Request):
    client = _client_ip(request)
    locked, remaining = is_locked(body.username, client)
    if locked:
        record(
            "auth_lockout",
            username=body.username,
            client=client,
            remaining_seconds=remaining,
        )
        raise HTTPException(
            status_code=429,
            detail=f"Too many failed attempts. Locked for {remaining}s (twin)",
            headers={"Retry-After": str(int(remaining) + 1)},
        )

    user = _STUB_USERS.get(body.username)
    if not user or not verify_password(body.password, user["hashed_password"]):
        now_locked, lock_secs = record_failure(body.username, client)
        record(
            "auth_failure",
            username=body.username,
            client=client,
            locked=now_locked,
        )
        if now_locked:
            raise HTTPException(
                status_code=429,
                detail=f"Too many failed attempts. Locked for {lock_secs}s (twin)",
                headers={"Retry-After": str(int(lock_secs))},
            )
        raise HTTPException(status_code=401, detail="Invalid credentials (twin)")

    record_success(body.username, client)
    access = create_access_token(user["username"], {"roles": user["roles"]})
    refresh = create_refresh_token(user["username"])
    record("auth_success", username=user["username"], roles=user["roles"], client=client)
    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        expires_in=settings.jwt_access_token_expire_minutes * 60,
    )


@app.post(f"{settings.api_prefix}/auth/refresh")
async def refresh(body: RefreshRequest):
    payload = decode_token(body.refresh_token, expected_type="refresh", check_blacklist=True)
    if not payload:
        record("auth_failure", reason="invalid_or_revoked_refresh")
        raise HTTPException(status_code=401, detail="Invalid, expired, or revoked refresh token (twin)")
    username = payload.get("sub", "")
    user = _STUB_USERS.get(username)
    if not user:
        record("auth_failure", username=username, reason="user_not_found")
        raise HTTPException(status_code=401, detail="User not found (twin)")
    # rotate: revoke old refresh jti
    revoke(payload.get("jti", ""), payload.get("exp"))
    access = create_access_token(username, {"roles": user["roles"]})
    new_refresh = create_refresh_token(username)
    record("auth_refresh", username=username)
    return {
        "access_token": access,
        "refresh_token": new_refresh,
        "token_type": "bearer",
        "expires_in": settings.jwt_access_token_expire_minutes * 60,
        "twin": True,
    }


@app.post(f"{settings.api_prefix}/auth/logout", response_model=MessageResponse)
async def logout(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    body: RefreshRequest | None = None,
):
    revoked = []
    if creds:
        payload = decode_token(creds.credentials, expected_type="access", check_blacklist=False)
        if payload and payload.get("jti"):
            revoke(payload["jti"], payload.get("exp"))
            revoked.append("access")
    # optional refresh in body
    if body and body.refresh_token:
        rp = decode_token(body.refresh_token, expected_type="refresh", check_blacklist=False)
        if rp and rp.get("jti"):
            revoke(rp["jti"], rp.get("exp"))
            revoked.append("refresh")
    record("auth_logout", revoked=revoked)
    return MessageResponse(
        message=f"Logged out (twin). Revoked: {revoked or ['none — send Bearer access token']}"
    )


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
    # Pydantic already enforces max lengths; extra guard
    if len(body.content) > settings.memory_max_content_chars:
        record("size_reject", path="/memory/remember", reason="content_too_long")
        raise HTTPException(status_code=413, detail="Content too large (twin)")
    entry = {
        "id": f"mem-{len(_memory_store)+1}",
        "content": body.content,
        "tags": body.tags[: settings.memory_max_tags],
        "owner": user.get("sub"),
        "verified": False,
        "twin": True,
    }
    _memory_store.append(entry)
    record("memory_write", owner=user.get("sub"), entry_id=entry["id"])
    return {"status": "stored", "entry": entry, "twin": True}


@app.get(f"{settings.api_prefix}/memory/recall")
async def recall(q: str = "", user: dict = Depends(get_current_user)):
    if len(q) > 512:
        raise HTTPException(status_code=400, detail="Query too long (twin)")
    results = [m for m in _memory_store if q.lower() in m["content"].lower()]
    record("memory_recall", query=q[:128], result_count=len(results), user=user.get("sub"))
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


@app.get(f"{settings.api_prefix}/audit/summary")
async def audit_summary(user: dict = Depends(require_admin)):
    return summary()


@app.get(f"{settings.api_prefix}/audit/export")
async def audit_export(
    limit: int = 5000,
    format: str = "json",
    user: dict = Depends(require_admin),
):
    events = get_events(limit=min(limit, 20_000))
    record("audit_export", by=user.get("sub"), count=len(events), format=format)

    if format == "jsonl":
        import json as _json

        body = "\n".join(_json.dumps(e, default=str) for e in events) + ("\n" if events else "")
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
            "version": settings.app_version,
            "exported_by": user.get("sub"),
            "event_count": len(events),
            "events": events,
        },
        headers={"X-KCN-Twin-Notice": "TWIN-TEST-LOG-NOT-PRODUCTION"},
    )
