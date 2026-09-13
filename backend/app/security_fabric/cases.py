"""Security Case aggregation model."""

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from app.security_fabric.evidence import EvidenceRecord
from app.security_fabric.models import SecurityEvent


class SecurityCase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: str = Field(default_factory=lambda: f"case-{uuid4().hex[:24]}")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "open"
    events: list[SecurityEvent] = Field(default_factory=list)
    evidence: list[EvidenceRecord] = Field(default_factory=list)
    threat: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    policy: str | None = None
    decision: str | None = None
    authorization: dict[str, Any] | None = None
    action: str | None = None
    outcome: str | None = None
    replay_reference: str | None = None
    verification_status: str = "NOT_MEASURED"
    human_authority: str | None = None

    @classmethod
    def from_events(cls, events: list[SecurityEvent], evidence: list[EvidenceRecord] | None = None) -> "SecurityCase":
        return cls(events=events, evidence=evidence or [])
