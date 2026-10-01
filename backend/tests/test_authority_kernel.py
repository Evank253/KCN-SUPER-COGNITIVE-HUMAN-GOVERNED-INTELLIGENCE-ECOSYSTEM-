"""KSI-ASI-001 authority-domain kernel tests.

These are kernel-level invariants. They deliberately do not claim ASI
qualification; ASI-00…15 adversarial execution belongs above this layer.
"""

from datetime import datetime, timedelta, timezone

import pytest

from app.security_fabric.authority import (
    AuthorizationEngine,
    AuthorizationRequest,
    AuthorityRegistry,
    DelegatedAuthority,
    DelegationEvent,
)


NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def grant(
    authority_id: str = "a1",
    *,
    issuer: str = "human:evan",
    recipient: str = "agent:a",
    actions: set[str] | None = None,
    capabilities: set[str] | None = None,
    parent: str | None = None,
    allow_subdelegation: bool = False,
    valid_until: datetime | None = None,
) -> DelegatedAuthority:
    return DelegatedAuthority(
        authority_id=authority_id,
        issuer=issuer,
        recipient=recipient,
        parent_authority=parent,
        capabilities=frozenset(capabilities or {"test.execute"}),
        permitted_actions=frozenset(actions or {"run.test"}),
        valid_from=NOW - timedelta(minutes=1),
        valid_until=valid_until,
        delegation_policy={"allow_subdelegation": allow_subdelegation},
        integrity_reference=f"sha256:{authority_id}",
    )


def event(authority: DelegatedAuthority, *, approved: bool = True) -> DelegationEvent:
    return DelegationEvent(
        event_id=f"evt-{authority.authority_id}",
        authority=authority,
        issued_at=NOW,
        human_approved=approved,
        approval_reference="approval-1" if approved else None,
        issuer_authenticated=True,
    )


def test_valid_human_delegation_allows_in_scope_action():
    registry = AuthorityRegistry()
    registry.apply_event(event(grant()))
    result = AuthorizationEngine().authorize(
        AuthorizationRequest(
            action_id="act-1",
            requesting_principal="agent:a",
            requested_action="run.test",
            requested_capability="test.execute",
            evaluated_at=NOW,
        ),
        registry.state,
    )
    assert result.decision == "ALLOW"
    assert result.authority_chain == ("a1",)
    assert len(result.evidence_reference) == 64


def test_scope_violation_escalates():
    registry = AuthorityRegistry()
    registry.apply_event(event(grant()))
    result = AuthorizationEngine().authorize(
        AuthorizationRequest(
            action_id="act-2",
            requesting_principal="agent:a",
            requested_action="delete.production",
            evaluated_at=NOW,
        ),
        registry.state,
    )
    assert result.decision == "ESCALATE"


def test_self_expansion_is_rejected():
    registry = AuthorityRegistry()
    registry.apply_event(event(grant()))
    with pytest.raises(ValueError, match="delegated actions exceed parent"):
        registry.apply_event(
            event(
                grant(
                    "a2",
                    issuer="agent:a",
                    recipient="agent:b",
                    parent="a1",
                    actions={"run.test", "delete.production"},
                    allow_subdelegation=True,
                )
            )
        )


def test_unauthorized_transfer_is_rejected():
    registry = AuthorityRegistry()
    registry.apply_event(event(grant()))
    with pytest.raises(ValueError, match="issuer does not match parent recipient"):
        registry.apply_event(
            event(
                grant(
                    "a2",
                    issuer="agent:attacker",
                    recipient="agent:b",
                    parent="a1",
                    allow_subdelegation=True,
                )
            )
        )


def test_fabricated_human_root_is_rejected():
    registry = AuthorityRegistry()
    with pytest.raises(ValueError, match="root delegation must originate from a human issuer"):
        registry.apply_event(event(grant("fake", issuer="agent:a")))


def test_missing_human_approval_is_rejected():
    registry = AuthorityRegistry()
    with pytest.raises(ValueError, match="human approval missing"):
        registry.apply_event(event(grant(), approved=False))


def test_revocation_dominates_prior_authorization():
    registry = AuthorityRegistry()
    registry.apply_event(event(grant()))
    before = AuthorizationEngine().authorize(
        AuthorizationRequest(
            action_id="act-3", requesting_principal="agent:a",
            requested_action="run.test", evaluated_at=NOW
        ), registry.state
    )
    assert before.decision == "ALLOW"

    registry.apply_event(
        DelegationEvent(
            event_id="revoke-a1",
            authority=grant(),
            issued_at=NOW,
            human_approved=True,
            approval_reference="approval-revoke",
            issuer_authenticated=True,
            event_type="REVOKE",
            target_authority_id="a1",
        )
    )
    after = AuthorizationEngine().authorize(
        AuthorizationRequest(
            action_id="act-4", requesting_principal="agent:a",
            requested_action="run.test", evaluated_at=NOW
        ), registry.state
    )
    assert after.decision == "DENY"
    assert "revoked" in after.decision_reason


def test_expiration_dominates_authorization():
    registry = AuthorityRegistry()
    registry.apply_event(event(grant(valid_until=NOW + timedelta(seconds=1))))
    result = AuthorizationEngine().authorize(
        AuthorizationRequest(
            action_id="act-5", requesting_principal="agent:a",
            requested_action="run.test", evaluated_at=NOW + timedelta(seconds=2)
        ), registry.state
    )
    assert result.decision == "DENY"


def test_reserved_action_never_becomes_autonomous_authority():
    registry = AuthorityRegistry(reserved_actions={"production.deploy"})
    with pytest.raises(ValueError, match="reserved human action"):
        registry.apply_event(
            event(grant(actions={"production.deploy"}))
        )


def test_capability_gain_does_not_change_authority():
    registry = AuthorityRegistry()
    registry.apply_event(event(grant()))
    before = registry.state
    with pytest.raises(ValueError):
        registry.apply_event(
            event(
                grant(
                    "a2", issuer="agent:a", recipient="agent:b", parent="a1",
                    capabilities={"test.execute", "production.deploy"},
                    allow_subdelegation=True,
                )
            )
        )
    assert registry.state == before


def test_authorization_engine_does_not_mutate_authority_state():
    registry = AuthorityRegistry()
    registry.apply_event(event(grant()))
    before = registry.state
    AuthorizationEngine().authorize(
        AuthorizationRequest(
            action_id="act-6", requesting_principal="agent:a",
            requested_action="run.test", evaluated_at=NOW
        ), before
    )
    assert registry.state == before


def test_execution_success_cannot_expand_authority_without_delegation_event():
    registry = AuthorityRegistry()
    registry.apply_event(event(grant()))
    before = registry.state
    # Simulated execution result is deliberately not an authority mutation.
    execution_result = {"success": True, "new_capabilities": {"production.deploy"}}
    assert execution_result["success"] is True
    assert registry.state == before
    assert "production.deploy" not in next(iter(registry.state.authorities.values())).capabilities
