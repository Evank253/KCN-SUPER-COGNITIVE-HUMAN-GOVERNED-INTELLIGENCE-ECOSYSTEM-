"""
Governance routes — policies and human approval workflows.
"""

import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/governance")


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class Policy(BaseModel):
    """A governance policy record."""

    id: str
    name: str
    description: str
    enabled: bool
    created_at: str
    updated_at: str


class PolicyListResponse(BaseModel):
    """Paginated list of governance policies."""

    policies: list[Policy]
    total: int


class ApprovalRequest(BaseModel):
    """Request body for submitting a human approval request."""

    action_type: str = Field(..., min_length=1, max_length=128)
    description: str = Field(..., min_length=1, max_length=1024)
    data: dict | None = None


class ApprovalResponse(BaseModel):
    """Response after submitting an approval request."""

    id: str
    status: str
    created_at: str


# ---------------------------------------------------------------------------
# Stub data (replaced by database layer in Phase 2)
# ---------------------------------------------------------------------------

_STUB_POLICIES = [
    Policy(
        id="pol-001",
        name="Human Approval Required for High-Risk Actions",
        description=(
            "All actions classified as high-risk must receive explicit human "
            "approval before execution."
        ),
        enabled=True,
        created_at="2026-08-01T00:00:00Z",
        updated_at="2026-08-01T00:00:00Z",
    ),
    Policy(
        id="pol-002",
        name="AI Output Verification Mandatory",
        description=(
            "All Intelligence Core outputs must pass through the Verification "
            "Core before entering the Knowledge Core."
        ),
        enabled=True,
        created_at="2026-08-01T00:00:00Z",
        updated_at="2026-08-01T00:00:00Z",
    ),
    Policy(
        id="pol-003",
        name="Audit Trail Immutability",
        description=(
            "Audit logs may not be modified or deleted once written. "
            "All audit events are retained for a minimum of 12 months."
        ),
        enabled=True,
        created_at="2026-08-01T00:00:00Z",
        updated_at="2026-08-01T00:00:00Z",
    ),
]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.get(
    "/policies",
    response_model=PolicyListResponse,
    status_code=status.HTTP_200_OK,
    summary="List governance policies",
)
async def list_policies() -> PolicyListResponse:
    """
    Return all active governance policies.

    Requires `admin` or `governance_viewer` role.
    Authentication and RBAC enforcement will be added in Phase 2.
    """
    return PolicyListResponse(policies=_STUB_POLICIES, total=len(_STUB_POLICIES))


@router.post(
    "/approvals",
    response_model=ApprovalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit approval request",
)
async def submit_approval(request: ApprovalRequest) -> ApprovalResponse:
    """
    Submit a request for human approval.

    Returns a pending approval record. Human reviewers will evaluate and
    approve or reject the request via the governance dashboard.
    Full workflow integration is planned for Phase 2.
    """
    approval_id = f"appr-{uuid.uuid4().hex[:12]}"
    created_at = datetime.now(timezone.utc).isoformat()

    logger.info(
        "Approval request submitted: id=%s action_type=%s",
        approval_id,
        request.action_type,
    )

    # TODO(Phase 2): Persist approval request to database and notify reviewers
    return ApprovalResponse(
        id=approval_id,
        status="pending",
        created_at=created_at,
    )
