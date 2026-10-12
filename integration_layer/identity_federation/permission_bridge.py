"""Permission evaluation that bridges identity and resource scopes."""

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Set
from pydantic import BaseModel, Field
from .unified_identity import IdentityType


class AccessDecision(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_HUMAN_APPROVAL = "require_human_approval"


class Permission(BaseModel):
    resource: str
    action: str
    effect: AccessDecision = AccessDecision.ALLOW
    conditions: Dict[str, str] = Field(default_factory=dict)


class PermissionBridge:
    def __init__(self) -> None:
        self._grants: Dict[str, Set[str]] = {}
        self._type_requirements: Dict[str, Set[IdentityType]] = {}
        self._human_gated: Set[str] = set()

    def grant(self, identity_id: str, resource: str, action: str) -> None:
        key = f"{resource}:{action}"
        self._grants.setdefault(identity_id, set()).add(key)

    def revoke(self, identity_id: str, resource: str, action: str) -> None:
        key = f"{resource}:{action}"
        if identity_id in self._grants:
            self._grants[identity_id].discard(key)

    def require_identity_type(self, resource: str, action: str, types: List[IdentityType]) -> None:
        key = f"{resource}:{action}"
        self._type_requirements[key] = set(types)

    def mark_human_gated(self, resource: str, action: str) -> None:
        self._human_gated.add(f"{resource}:{action}")

    def evaluate(self, identity_id: str, identity_type: IdentityType, resource: str, action: str) -> AccessDecision:
        key = f"{resource}:{action}"
        if key in self._human_gated and identity_type != IdentityType.HUMAN:
            return AccessDecision.REQUIRE_HUMAN_APPROVAL
        required_types = self._type_requirements.get(key)
        if required_types and identity_type not in required_types:
            return AccessDecision.DENY
        grants = self._grants.get(identity_id, set())
        if key in grants or f"{resource}:*" in grants or f"*:{action}" in grants or "*:*" in grants:
            return AccessDecision.ALLOW
        return AccessDecision.DENY
