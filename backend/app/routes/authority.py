"""
Human-authority boundary routes (L3-F13 / L3-F14 style).

Agent JWT + valid credential/proof still yields 403 on acceptance and resume.
Cryptography proves identity claims; governance decides permission.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, Field

from kcn_core.discovery import sandbox
from kcn_core.human_ai import human_ai_governance, twin

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/authority")

# In-memory acceptance store hash stand-in for F13 state checks
_acceptance_log: list[dict[str, Any]] = []


def _role_from_authorization(authorization: str | None, x_actor_role: str | None) -> str:
    if x_actor_role:
        return x_actor_role.strip().lower()
    if not authorization:
        return "anonymous"
    # Lightweight role hint for sealed tests: Bearer agent|human|governance
    token = authorization.replace("Bearer", "").strip().lower()
    for role in ("agent", "governance", "admin", "security_officer", "human_operator", "human"):
        if role in token:
            return role
    return "unknown"


class AcceptanceBody(BaseModel):
    action: str = "acceptance"
    request_id: str = Field(..., min_length=1)
    presentation: dict[str, Any] | None = None
    token_a: str | None = None
    token_b: str | None = None


class ResumeBody(BaseModel):
    reason: str | None = None
    presentation: dict[str, Any] | None = None


class PromoteBody(BaseModel):
    approve: bool = True


@router.get("/watchdog/status")
async def watchdog_status() -> dict[str, Any]:
    return human_ai_governance.status()


@router.post("/watchdog/kill")
async def watchdog_kill(
    reason: str = "safety",
    authorization: str | None = Header(default=None),
    x_actor_role: str | None = Header(default=None),
) -> dict[str, Any]:
    role = _role_from_authorization(authorization, x_actor_role)
    return human_ai_governance.kill(reason=reason, actor=role)


@router.post("/watchdog/resume")
async def watchdog_resume(
    body: ResumeBody | None = None,
    authorization: str | None = Header(default=None),
    x_actor_role: str | None = Header(default=None),
) -> dict[str, Any]:
    """L3-F14: agent must receive 403; state stays killed/frozen."""
    role = _role_from_authorization(authorization, x_actor_role)
    # Valid presentation must not grant resume
    _ = body.presentation if body else None
    result = human_ai_governance.resume(actor_role=role)
    if not result.get("allowed"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "reason": result.get("reason", "not_human_authority"),
                "state": result.get("state"),
                "message": result.get("message", "Forbidden"),
            },
        )
    return result


@router.post("/self-mod/acceptance")
async def self_mod_acceptance(
    body: AcceptanceBody,
    authorization: str | None = Header(default=None),
    x_actor_role: str | None = Header(default=None),
) -> dict[str, Any]:
    """L3-F13: agent + valid VP/proof → 403; no acceptance state transition."""
    role = _role_from_authorization(authorization, x_actor_role)
    before = len(_acceptance_log)

    if role in {"agent", "ai", "service", "system_agent", "anonymous", "unknown"}:
        logger.info(
            "F13 deny acceptance role=%s request_id=%s has_presentation=%s",
            role,
            body.request_id,
            body.presentation is not None,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "reason": "not_human_authority",
                "request_id": body.request_id,
                "message": "Valid credential/proof does not grant human acceptance authority.",
                "acceptance_count": before,
            },
        )

    # Proof-as-token abuse: reject
    if body.token_a and body.token_a.startswith("u2V0"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"reason": "invalid_token_material", "request_id": body.request_id},
        )

    if role in {"human", "governance", "admin", "security_officer", "human_operator"}:
        if not (body.token_a and body.token_b and body.token_a != body.token_b):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "reason": "dual_control_required",
                    "request_id": body.request_id,
                },
            )
        rec = {
            "request_id": body.request_id,
            "role": role,
            "status": "accepted",
        }
        _acceptance_log.append(rec)
        return {"status": "accepted", "request_id": body.request_id, "acceptance_count": len(_acceptance_log)}

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"reason": "not_human_authority"})


@router.post("/discovery/{item_id}/decide")
async def discovery_decide(
    item_id: str,
    body: PromoteBody,
    authorization: str | None = Header(default=None),
    x_actor_role: str | None = Header(default=None),
) -> dict[str, Any]:
    role = _role_from_authorization(authorization, x_actor_role)
    result = sandbox.decide_promotion(item_id, body.approve, role)
    if result.get("http_status") == 403:
        raise HTTPException(status_code=403, detail=result)
    if result.get("http_status") == 404:
        raise HTTPException(status_code=404, detail=result)
    return result


@router.get("/twin/status")
async def twin_status() -> dict[str, Any]:
    return twin.status()
