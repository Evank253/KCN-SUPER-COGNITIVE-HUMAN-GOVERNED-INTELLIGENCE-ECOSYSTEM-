from datetime import datetime, timedelta, timezone

import pytest

from app.security_fabric.adapters import ADAPTERS, AdapterError, SuricataAdapter, ZeekAdapter
from app.security_fabric.cases import SecurityCase
from app.security_fabric.correlation import CorrelationEngine
from app.security_fabric.evidence import build_evidence
from app.security_fabric.models import SecurityEvent
from app.security_fabric.normalize import Normalizer


def make_event(event_id: str, observable: dict[str, str], offset: int = 0) -> SecurityEvent:
    return SecurityEvent(
        event_id=event_id,
        source="test",
        timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=offset),
        event_type="test",
        observable=observable,
    )


def test_security_event_rejects_unknown_fields():
    with pytest.raises(Exception):
        SecurityEvent(
            event_id="evt-1",
            source="test",
            timestamp=datetime.now(timezone.utc),
            event_type="test",
            unknown_field=True,
        )


def test_security_event_confidence_is_bounded():
    with pytest.raises(Exception):
        SecurityEvent(
            event_id="evt-1",
            source="test",
            timestamp=datetime.now(timezone.utc),
            event_type="test",
            confidence=1.1,
        )


def test_all_selected_adapters_are_registered():
    expected = {
        "zeek", "suricata", "wazuh", "velociraptor", "arkime",
        "opencti", "misp", "sigma", "yara", "falco",
    }
    assert expected == set(ADAPTERS)


def test_suricata_adapter_normalizes_to_canonical_event():
    result = SuricataAdapter.adapt({
        "timestamp": "2026-01-01T00:00:00Z",
        "event_type": "alert",
        "src_ip": "10.0.0.1",
        "src_port": 1234,
        "dest_ip": "10.0.0.2",
        "dest_port": 443,
        "alert": {"signature_id": 1001, "signature": "test alert", "category": "test"},
    })
    assert result.event.source == "suricata"
    assert result.event.observable["src_ip"] == "10.0.0.1"
    assert result.event.detection == "test alert"
    assert len(result.raw_hash) == 64


def test_zeek_adapter_preserves_network_observables():
    result = ZeekAdapter.adapt({
        "ts": 1767225600,
        "uid": "C-test",
        "id.orig_h": "10.0.0.1",
        "id.orig_p": 1234,
        "id.resp_h": "10.0.0.2",
        "id.resp_p": 443,
        "service": "ssl",
    })
    assert result.event.source == "zeek"
    assert result.event.observable["dst_ip"] == "10.0.0.2"
    assert result.event.event_type == "ssl"


def test_normalizer_removes_null_observables():
    event = make_event("evt-1", {"ip": "10.0.0.1", "port": None})
    normalized = Normalizer().normalize(event)
    assert normalized.observable == {"ip": "10.0.0.1"}


def test_correlation_groups_shared_observable_within_window():
    events = [
        make_event("a", {"src_ip": "10.0.0.1"}, 0),
        make_event("b", {"src_ip": "10.0.0.1"}, 30),
        make_event("c", {"src_ip": "10.0.0.9"}, 30),
    ]
    groups = CorrelationEngine(window_seconds=300).correlate(events)
    assert [[event.event_id for event in group] for group in groups] == [["a", "b"], ["c"]]


def test_correlation_does_not_merge_outside_window():
    events = [make_event("a", {"src_ip": "10.0.0.1"}, 0), make_event("b", {"src_ip": "10.0.0.1"}, 301)]
    groups = CorrelationEngine(window_seconds=300).correlate(events)
    assert len(groups) == 2


def test_evidence_contains_canonical_hash_and_provenance():
    event = make_event("evt-1", {"ip": "10.0.0.1"})
    evidence = build_evidence(event)
    assert evidence.event_id == event.event_id
    assert len(evidence.artifact_hash or "") == 64
    assert len(evidence.provenance["canonical_hash"]) == 64


def test_security_case_preserves_events_and_evidence():
    event = make_event("evt-1", {"ip": "10.0.0.1"})
    evidence = build_evidence(event)
    case = SecurityCase.from_events([event], [evidence])
    assert case.events[0].event_id == "evt-1"
    assert case.evidence[0].evidence_id == evidence.evidence_id
    assert case.verification_status == "NOT_MEASURED"
