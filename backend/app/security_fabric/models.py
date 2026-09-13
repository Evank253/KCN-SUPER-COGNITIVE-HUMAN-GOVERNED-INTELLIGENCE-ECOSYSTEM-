"""Canonical KCN Security Fabric event model.

Vendor-specific events must be converted to this model before entering KCN.
"""

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SecurityEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    event_id: str
    source: str
    sensor_id: str | None = None
    agent_id: str | None = None
    actor_id: str | None = None
    timestamp: datetime
    event_type: str
    observable: dict[str, Any] = Field(default_factory=dict)
    entity: dict[str, Any] = Field(default_factory=dict)
    relationship: dict[str, Any] = Field(default_factory=dict)
    detection: str | None = None
    threat: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    policy: str | None = None
    decision: str | None = None
    action: str | None = None
    outcome: str | None = None
    artifact: dict[str, Any] | None = None
    artifact_hash: str | None = None
    provenance: dict[str, Any] = Field(default_factory=dict)
    evidence_level: str = "E1"
    replay_reference: str | None = None
    verification_status: str = "NOT_MEASURED"
    human_authority: str | None = None

    @field_validator("timestamp")
    @classmethod
    def normalize_timestamp(cls, value: datetime) -> datetime:
        """Require a deterministic UTC-aware timestamp for correlation/replay."""
        if value.tzinfo is None or value.utcoffset() is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    @classmethod
    def now(cls, **kwargs: Any) -> "SecurityEvent":
        return cls(timestamp=datetime.now(timezone.utc), **kwargs)
