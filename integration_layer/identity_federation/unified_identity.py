"""Unified identity across human, agent, and service principals."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
import uuid


class IdentityType(str, Enum):
    HUMAN = "human"
    AGENT = "agent"
    SERVICE = "service"
    SYSTEM = "system"


class IdentityRecord(BaseModel):
    identity_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    identity_type: IdentityType
    display_name: str
    external_ids: Dict[str, str] = Field(default_factory=dict)
    attributes: Dict[str, str] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    active: bool = True


class UnifiedIdentity:
    def __init__(self) -> None:
        self._identities: Dict[str, IdentityRecord] = {}
        self._external_index: Dict[str, str] = {}

    def register(self, record: IdentityRecord) -> IdentityRecord:
        self._identities[record.identity_id] = record
        for provider, value in record.external_ids.items():
            self._external_index[f"{provider}:{value}"] = record.identity_id
        return record

    def get(self, identity_id: str) -> Optional[IdentityRecord]:
        return self._identities.get(identity_id)

    def resolve_external(self, provider: str, value: str) -> Optional[IdentityRecord]:
        identity_id = self._external_index.get(f"{provider}:{value}")
        if identity_id is None:
            return None
        return self._identities.get(identity_id)

    def list_by_type(self, identity_type: IdentityType) -> List[IdentityRecord]:
        return [r for r in self._identities.values() if r.identity_type == identity_type]

    def deactivate(self, identity_id: str) -> None:
        if identity_id in self._identities:
            self._identities[identity_id].active = False
