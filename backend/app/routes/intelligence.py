"""
Intelligence Core routes — analysis and reasoning requests.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Literal

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/intelligence")

IntelligenceModule = Literal[
    "research", "reasoning", "planning", "creative", "engineering", "analysis", "learning"
]


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class AnalysisRequest(BaseModel):
    """Request body for the Intelligence Core."""

    query: str = Field(..., min_length=1, max_length=4096)
    context: dict[str, Any] | None = None
    module: IntelligenceModule = "analysis"


class AnalysisResponse(BaseModel):
    """Intelligence Core analysis response."""

    id: str
    module: str
    status: str
    result: dict[str, Any] | None
    created_at: str


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit analysis request",
)
async def analyze(request: AnalysisRequest) -> AnalysisResponse:
    """
    Submit a request to the Intelligence Core for analysis.

    The output will be queued for Verification Core evaluation before
    results are made available. Full module implementations are planned
    for Phase 2.
    """
    result_id = f"intel-{uuid.uuid4().hex[:12]}"
    created_at = datetime.now(timezone.utc).isoformat()

    logger.info(
        "Intelligence request created: id=%s module=%s",
        result_id,
        request.module,
    )

    # TODO(Phase 2): Route to appropriate intelligence module and process asynchronously
    return AnalysisResponse(
        id=result_id,
        module=request.module,
        status="pending_verification",
        result=None,
        created_at=created_at,
    )
