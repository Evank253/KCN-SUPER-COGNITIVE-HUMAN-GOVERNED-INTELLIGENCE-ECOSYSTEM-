"""Small, explicit authority-domain kernel for KSI-ASI-001.

Authority is delegated by a superior issuer and is never inferred from
capability, evidence, qualification, confidence, or successful execution.

The registry owns authority state. The authorization engine only reads that
state and produces an immutable decision; execution must not mutate it.
"""

from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
from typing import Any, Iterable, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


Decision = Literal["ALLOW", "DENY", "ESCALATE"]


def _canonical_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return sha256(payload.encode("utf-8")).hexdigest()


class DelegatedAuthority(BaseModel):
    """An authority grant with an explicit chain and bounded scope."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    authority_id: str
    issuer: str
    recipient: str
    parent_authority: str | None = None
    capabilities: frozenset[str] = frozenset()
    permitted_actions: frozenset[str] = frozenset()
    scope: dict[str, Any] = Field(default_factory=dict)
    constraints: dict[str, Any] = Field(default_factory=dict)
    resource_limits: dict[str, Any] = Field(default_factory=dict)
    valid_from: datetime
    valid_until: datetime | None = None
    revocation_state: Literal["ACTIVE", "REVOKED"] = "ACTIVE"
    delegation_policy: dict[str, Any] = Field(default_factory=dict)
    provenance: dict[str, Any] = Field(default_factory=dict)
    integrity_reference: str

    @field_validator("valid_until")
    @classmethod
    def _valid_window(cls, value: datetime | None, info: Any) -> datetime | None:
        valid_from = info.data.get("valid_from")
        if value is not None and valid_from is not None and value <= valid_from:
            raise ValueError("valid_until must be later than valid_from")
        return value


class DelegationEvent(BaseModel):
    """The only input that may change authority state."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    event_id: str
    authority: DelegatedAuthority
    issued_at: datetime
    human_approved: bool = False
    approval_reference: str | None = None
    issuer_authenticated: bool = False
    event_type: Literal["DELEGATE", "REVOKE"] = "DELEGATE"
    target_authority_id: str | None = None


class AuthorizationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    action_id: str
    requesting_principal: str
    requested_action: str
    requested_capability: str | None = None
    scope: dict[str, Any] = Field(default_factory=dict)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AuthorizationDecision(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    decision_id: str
    action_id: str
    requesting_principal: str
    authority_chain: tuple[str, ...]
    effective_authority: str | None
    requested_capability: str | None
    requested_action: str
    scope_result: bool
    constraint_result: bool
    temporal_result: bool
    revocation_result: bool
    reserved_boundary_result: bool
    decision: Decision
    decision_reason: str
    evaluated_at: datetime
    evidence_reference: str


class AuthorityState(BaseModel):
    """Read-only snapshot supplied to the authorization engine."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    authorities: dict[str, DelegatedAuthority] = Field(default_factory=dict)
    reserved_actions: frozenset[str] = frozenset()


class DelegationValidator:
    """Validates delegation events without owning authority state."""

    def __init__(self, reserved_actions: Iterable[str] = ()) -> None:
        self._reserved_actions = frozenset(reserved_actions)

    def validate(self, event: DelegationEvent, state: AuthorityState) -> tuple[bool, str]:
        authority = event.authority

        if event.event_type == "REVOKE":
            target = event.target_authority_id or authority.authority_id
            if target not in state.authorities:
                return False, "target authority does not exist"
            return True, "revocation event valid"

        if not event.issuer_authenticated:
            return False, "issuer authentication missing"
        if not event.human_approved:
            return False, "human approval missing for authority-changing event"
        if not event.approval_reference:
            return False, "approval reference missing"
        if authority.authority_id in state.authorities:
            return False, "authority_id already exists"

        if authority.permitted_actions & self._reserved_actions:
            return False, "reserved human action cannot be delegated"

        if authority.parent_authority is None:
            if not authority.issuer.startswith("human:"):
                return False, "root delegation must originate from a human issuer"
            return True, "valid human-originated delegation"

        parent = state.authorities.get(authority.parent_authority)
        if parent is None:
            return False, "parent authority not found"
        if parent.revocation_state == "REVOKED":
            return False, "parent authority revoked"

        if authority.issuer != parent.recipient:
            return False, "issuer does not match parent recipient"

        if not authority.capabilities <= parent.capabilities:
            return False, "delegated capabilities exceed parent authority"
        if not authority.permitted_actions <= parent.permitted_actions:
            return False, "delegated actions exceed parent authority"

        delegation_policy = parent.delegation_policy
        if delegation_policy.get("allow_subdelegation") is not True:
            return False, "parent does not permit subdelegation"

        return True, "valid bounded subdelegation"

    def apply(self, event: DelegationEvent, state: AuthorityState) -> AuthorityState:
        valid, reason = self.validate(event, state)
        if not valid:
            raise ValueError(reason)

        authorities = dict(state.authorities)
        if event.event_type == "REVOKE":
            target = event.target_authority_id or event.authority.authority_id
            existing = authorities[target]
            authorities[target] = existing.model_copy(update={"revocation_state": "REVOKED"})
        else:
            authorities[event.authority.authority_id] = event.authority
        return AuthorityState(authorities=authorities, reserved_actions=state.reserved_actions)


class AuthorityResolver:
    """Resolves an effective chain without changing authority state."""

    def resolve(self, principal: str, state: AuthorityState) -> tuple[DelegatedAuthority, ...]:
        current = next(
            (a for a in state.authorities.values() if a.recipient == principal),
            None,
        )
        if current is None:
            return ()

        chain: list[DelegatedAuthority] = []
        seen: set[str] = set()
        while current is not None:
            if current.authority_id in seen:
                raise ValueError("authority cycle detected")
            seen.add(current.authority_id)
            chain.append(current)
            current = (
                state.authorities.get(current.parent_authority)
                if current.parent_authority
                else None
            )
        return tuple(chain)


class AuthorizationEngine:
    """Pure authorization evaluation over an immutable authority snapshot."""

    def __init__(self, resolver: AuthorityResolver | None = None) -> None:
        self._resolver = resolver or AuthorityResolver()

    def authorize(self, request: AuthorizationRequest, state: AuthorityState) -> AuthorizationDecision:
        chain = self._resolver.resolve(request.requesting_principal, state)
        now = request.evaluated_at

        if not chain:
            return self._decision(
                request, (), None, False, False, False, False, True,
                "no delegated authority found", "DENY",
            )

        effective = chain[0]
        temporal = effective.valid_from <= now and (
            effective.valid_until is None or now <= effective.valid_until
        )
        not_revoked = all(a.revocation_state == "ACTIVE" for a in chain)
        reserved = request.requested_action not in state.reserved_actions
        scope = request.requested_action in effective.permitted_actions
        capability = (
            request.requested_capability is None
            or request.requested_capability in effective.capabilities
        )
        constraints = self._constraints_satisfied(effective, request)
        allowed = temporal and not_revoked and reserved and scope and capability and constraints

        if not reserved:
            decision, reason = "ESCALATE", "reserved human authority boundary"
        elif not temporal:
            decision, reason = "DENY", "authority outside temporal validity"
        elif not not_revoked:
            decision, reason = "DENY", "authority chain contains revoked authority"
        elif not scope:
            decision, reason = "ESCALATE", "requested action outside delegated scope"
        elif not capability:
            decision, reason = "DENY", "requested capability not delegated"
        elif not constraints:
            decision, reason = "DENY", "delegated constraints not satisfied"
        elif allowed:
            decision, reason = "ALLOW", "valid authority chain covers requested action"
        else:
            decision, reason = "DENY", "authorization conditions failed"

        evidence = {
            "action_id": request.action_id,
            "principal": request.requesting_principal,
            "authority_chain": [a.authority_id for a in chain],
            "effective_authority": effective.authority_id,
            "decision": decision,
            "reason": reason,
            "evaluated_at": now.isoformat(),
        }
        return self._decision(
            request,
            tuple(a.authority_id for a in chain),
            effective.authority_id,
            scope and capability,
            constraints,
            temporal,
            not_revoked,
            reserved,
            reason,
            decision,
            _canonical_hash(evidence),
        )

    @staticmethod
    def _constraints_satisfied(
        authority: DelegatedAuthority, request: AuthorizationRequest
    ) -> bool:
        required = authority.constraints.get("required_scope")
        if required is None:
            return True
        return all(request.scope.get(k) == v for k, v in required.items())

    @staticmethod
    def _decision(
        request: AuthorizationRequest,
        chain: tuple[str, ...],
        effective: str | None,
        scope: bool,
        constraints: bool,
        temporal: bool,
        revocation: bool,
        reserved: bool,
        reason: str,
        decision: Decision,
        evidence_reference: str | None = None,
    ) -> AuthorizationDecision:
        evidence = evidence_reference or _canonical_hash({
            "action_id": request.action_id,
            "decision": decision,
            "reason": reason,
        })
        return AuthorizationDecision(
            decision_id=f"authz-{_canonical_hash((request.action_id, request.evaluated_at.isoformat(), decision))[:24]}",
            action_id=request.action_id,
            requesting_principal=request.requesting_principal,
            authority_chain=chain,
            effective_authority=effective,
            requested_capability=request.requested_capability,
            requested_action=request.requested_action,
            scope_result=scope,
            constraint_result=constraints,
            temporal_result=temporal,
            revocation_result=revocation,
            reserved_boundary_result=reserved,
            decision=decision,
            decision_reason=reason,
            evaluated_at=request.evaluated_at,
            evidence_reference=evidence,
        )


class AuthorityRegistry:
    """Minimal state owner; all mutations require a separately validated event."""

    def __init__(self, reserved_actions: Iterable[str] = ()) -> None:
        self._state = AuthorityState(reserved_actions=frozenset(reserved_actions))
        self._validator = DelegationValidator(reserved_actions)

    @property
    def state(self) -> AuthorityState:
        return self._state

    def apply_event(self, event: DelegationEvent) -> AuthorityState:
        self._state = self._validator.apply(event, self._state)
        return self._state
