"""
Verification Core routes — retrieve verification results.
"""

import logging

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/verification")


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class VerificationCheck(BaseModel):
    """Result of a single verification check."""

    type: str
    passed: bool
    notes: str | None = None


class VerificationResult(BaseModel):
    """Full verification result for an intelligence output."""

    id: str
    intelligence_result_id: str
    status: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    checks: list[VerificationCheck]
    verified_at: str | None = None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.get(
    "/results/{result_id}",
    response_model=VerificationResult,
    status_code=status.HTTP_200_OK,
    summary="Get verification result",
)
async def get_verification_result(result_id: str) -> VerificationResult:
    """
    Retrieve verification results for an intelligence output.

    Returns the full verification record including individual check results
    and an overall confidence score.
    Full verification pipeline is planned for Phase 3.
    """
    if not result_id.startswith("intel-"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No verification result found for result_id={result_id}",
        )

    # TODO(Phase 3): Retrieve from Verification Core database
    return VerificationResult(
        id=f"verif-{result_id[6:]}",
        intelligence_result_id=result_id,
        status="stub_pending",
        confidence_score=0.0,
        checks=[
            VerificationCheck(
                type="logic_validation",
                passed=False,
                notes="Verification pipeline not yet implemented (Phase 3).",
            )
        ],
        verified_at=None,
    )
