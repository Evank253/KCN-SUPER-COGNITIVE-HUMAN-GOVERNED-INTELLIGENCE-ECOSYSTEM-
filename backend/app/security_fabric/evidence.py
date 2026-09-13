"""Evidence and provenance hooks for Security Fabric events."""

import json
from hashlib import sha256
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.security_fabric.models import SecurityEvent


class EvidenceRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    evidence_id: str
    event_id: str
    evidence_level: str
    artifact_hash: str | None
    provenance: dict[str, Any]
    source: str


def build_evidence(event: SecurityEvent, *, raw_hash: str | None = None) -> EvidenceRecord:
    payload = {
        "event_id": event.event_id,
        "source": event.source,
        "timestamp": event.timestamp.isoformat(),
        "event_type": event.event_type,
        "observable": event.observable,
        "detection": event.detection,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    digest = raw_hash or sha256(canonical.encode("utf-8")).hexdigest()
    evidence_id = f"evidence-{sha256(f'{event.event_id}:{digest}'.encode()).hexdigest()[:24]}"
    provenance = {**event.provenance, "canonical_hash": sha256(canonical.encode("utf-8")).hexdigest()}
    return EvidenceRecord(
        evidence_id=evidence_id,
        event_id=event.event_id,
        evidence_level=event.evidence_level,
        artifact_hash=digest,
        provenance=provenance,
        source=event.source,
    )
