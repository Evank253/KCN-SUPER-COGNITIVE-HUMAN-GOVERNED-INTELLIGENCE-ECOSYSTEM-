"""
Governance routes — policies and human approval workflows.
"""

import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.security_fabric.governance_store import GovernanceStore

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/governance")
_store = GovernanceStore()


class Policy(BaseModel):
    id: str
    name: str
    description: str
    enabled: bool
    created_at: str
    updated_at: str


class PolicyListResponse(BaseModel):
    policies: list[Policy]
    total: int


class ApprovalRequest(BaseModel):
    """Submit a request; case_id binds authorization to a SecurityCase."""

    action_type: str = Field(..., min_length=1, max_length=128)
    description: str = Field(..., min_length=1, max_length=1024)
    case_id: str | None = Field(default=None, min_length=1, max_length=128)
    data: dict | None = None


class ApprovalResponse(BaseModel):
    id: str
    status: str
    created_at: str
    case_id: str | None = None
    human_authority: str | None = None


class ApprovalDecision(BaseModel):
    status: str = Field(..., pattern="^(approved|rejected)$")
    human_authority: str = Field(..., min_length=1, max_length=256)


_STUB_POLICIES = [
    Policy(
        id="pol-001",
        name="Human Approval Required for High-Risk Actions",
        description="All actions classified as high-risk must receive explicit human approval before execution.",
        enabled=True,
        created_at="2026-08-01T00:00:00Z",
        updated_at="2026-08-01T00:00:00Z",
    ),
    Policy(
        id="pol-002",
        name="AI Output Verification Mandatory",
        description="All Intelligence Core outputs must pass through the Verification Core before entering the Knowledge Core.",
        enabled=True,
        created_at="2026-08-01T00:00:00Z",
        updated_at="2026-08-01T00:00:00Z",
    ),
    Policy(
        id="pol-003",
        name="Audit Trail Immutability",
        description="Audit logs may not be modified or deleted once written. All audit events are retained for a minimum of 12 months.",
        enabled=True,
        created_at="2026-08-01T00:00:00Z",
        updated_at="2026-08-01T00:00:00Z",
    ),
]


@router.get("/policies", response_model=PolicyListResponse, status_code=status.HTTP_200_OK)
async def list_policies() -> PolicyListResponse:
    """Return all active governance policies."""
    return PolicyListResponse(policies=_STUB_POLICIES, total=len(_STUB_POLICIES))


@router.post("/approvals", response_model=ApprovalResponse, status_code=status.HTTP_201_CREATED)
async def submit_approval(request: ApprovalRequest) -> ApprovalResponse:
    """Persist a pending approval request; it is not authorization."""
    approval_id = f"appr-{uuid.uuid4().hex[:12]}"
    record = _store.create(
        approval_id=approval_id,
        case_id=request.case_id,
        action_type=request.action_type,
        description=request.description,
        data=request.data,
    )
    logger.info("Approval request submitted: id=%s action_type=%s case_id=%s", approval_id, request.action_type, request.case_id)
    return ApprovalResponse(
        id=approval_id,
        status=record["status"],
        created_at=record["created_at"],
        case_id=record["case_id"],
    )


@router.get("/approvals/{approval_id}", response_model=ApprovalResponse)
async def get_approval(approval_id: str) -> ApprovalResponse:
    record = _store.get(approval_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="approval not found")
    return ApprovalResponse(
        id=approval_id,
        status=record["status"],
        created_at=record["created_at"],
        case_id=record.get("case_id"),
        human_authority=record.get("human_authority"),
    )


@router.post("/approvals/{approval_id}/decision", response_model=ApprovalResponse)
async def decide_approval(approval_id: str, decision: ApprovalDecision) -> ApprovalResponse:
    """Record an explicit human decision; only this transition supplies authority."""
    try:
        record = _store.decide(approval_id, decision.status, decision.human_authority)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="approval not found")
    return ApprovalResponse(
        id=approval_id,
        status=record["status"],
        created_at=record["created_at"],
        case_id=record.get("case_id"),
        human_authority=record.get("human_authority"),
    )
