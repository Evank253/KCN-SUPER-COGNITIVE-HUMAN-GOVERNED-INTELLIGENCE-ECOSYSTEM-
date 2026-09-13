"""Normalization pipeline for canonical KCN security events."""

from collections.abc import Iterable

from app.security_fabric.models import SecurityEvent


class Normalizer:
    """Apply deterministic, vendor-independent normalization rules."""

    def normalize(self, event: SecurityEvent) -> SecurityEvent:
        observable = {str(k): v for k, v in event.observable.items() if v is not None}
        entity = {str(k): v for k, v in event.entity.items() if v is not None}
        relationship = {str(k): v for k, v in event.relationship.items() if v is not None}
        return event.model_copy(update={
            "observable": observable,
            "entity": entity,
            "relationship": relationship,
        })

    def normalize_many(self, events: Iterable[SecurityEvent]) -> list[SecurityEvent]:
        return [self.normalize(event) for event in events]
