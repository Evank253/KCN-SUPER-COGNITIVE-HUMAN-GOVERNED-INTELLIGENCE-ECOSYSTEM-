from datetime import datetime, timedelta, timezone

import pytest

from app.security_fabric.adapters import ADAPTERS, OpenCTIAdapter, SuricataAdapter, ZeekAdapter
from app.security_fabric.cases import SecurityCase
from app.security_fabric.correlation import CorrelationEngine
from app.security_fabric.evidence import build_evidence
from app.security_fabric.models import SecurityEvent
from app.security_fabric.normalize import Normalizer


def make_event(event_id: str, observable: dict, offset: int = 0) -> SecurityEvent:
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


def test_security_event_normalizes_naive_timestamp_to_utc():
    event = SecurityEvent(
        event_id="evt-1", source="test", timestamp=datetime(2026, 1, 1), event_type="test"
    )
    assert event.timestamp.tzinfo == timezone.utc


def test_all_selected_adapters_are_registered():
    expected = {
        "zeek", "suricata", "wazuh", "velociraptor", "arkime",
        "opencti", "misp", "sigma", "yara", "falco",
    }
    assert expected == set(ADAPTERS)


def test_suricata_adapter_normalizes_to_canonical_event():
    result = SuricataAdapter.adapt({
        "timestamp": "2026-01-01T00:00:00Z", "event_type": "alert",
        "src_ip": "10.0.0.1", "src_port": 1234, "dest_ip": "10.0.0.2", "dest_port": 443,
        "alert": {"signature_id": 1001, "signature": "test alert", "category": "test"},
    })
    assert result.event.source == "suricata"
    assert result.event.observable["src_ip"] == "10.0.0.1"
    assert result.event.detection == "test alert"
    assert len(result.raw_hash) == 64


def test_zeek_adapter_preserves_network_observables():
    result = ZeekAdapter.adapt({
        "ts": 1767225600, "uid": "C-test", "id.orig_h": "10.0.0.1", "id.orig_p": 1234,
        "id.resp_h": "10.0.0.2", "id.resp_p": 443, "service": "ssl",
    })
    assert result.event.source == "zeek"
    assert result.event.observable["dst_ip"] == "10.0.0.2"
    assert result.event.event_type == "ssl"


def test_opencti_ipv4_sco_becomes_kcn_ip_observable():
    result = OpenCTIAdapter.adapt({
        "id": "ipv4-addr--123", "type": "ipv4-addr", "value": "10.0.0.25",
        "confidence": 80, "timestamp": "2026-01-01T00:00:00Z",
    })
    assert result.event.observable["ip"] == "10.0.0.25"
    assert result.event.observable["stix_id"] == "ipv4-addr--123"
    assert result.event.confidence == pytest.approx(0.8)


def test_opencti_relationship_is_preserved_not_joined():
    result = OpenCTIAdapter.adapt({
        "id": "relationship--123", "type": "relationship",
        "source_ref": "indicator--1", "target_ref": "ipv4-addr--2",
        "relationship_type": "indicates", "timestamp": "2026-01-01T00:00:00Z",
    })
    assert result.event.relationship == {
        "source_ref": "indicator--1", "target_ref": "ipv4-addr--2", "relationship_type": "indicates"
    }
    assert "source_ref" not in result.event.observable


def test_normalizer_removes_null_observables():
    event = make_event("evt-1", {"ip": "10.0.0.1", "port": None})
    normalized = Normalizer().normalize(event)
    assert normalized.observable == {"ip": "10.0.0.1"}


def test_correlation_groups_shared_allowed_observable_within_window():
    events = [
        make_event("a", {"src_ip": "10.0.0.1"}, 0),
        make_event("b", {"src_ip": "10.0.0.1"}, 30),
        make_event("c", {"src_ip": "10.0.0.9"}, 30),
    ]
    groups = CorrelationEngine(window_seconds=300).correlate(events)
    assert [[event.event_id for event in group] for group in groups] == [["a", "b"], ["c"]]


def test_correlation_does_not_merge_outside_origin_window():
    events = [
        make_event("a", {"src_ip": "10.0.0.1"}, 0),
        make_event("b", {"src_ip": "10.0.0.1"}, 290),
        make_event("c", {"src_ip": "10.0.0.1"}, 580),
    ]
    groups = CorrelationEngine(window_seconds=300).correlate(events)
    assert [[event.event_id for event in group] for group in groups] == [["a", "b"], ["c"]]


def test_correlation_does_not_merge_shared_dst_port_only():
    events = [
        make_event("a", {"src_ip": "10.0.0.1", "dst_port": 443}, 0),
        make_event("b", {"src_ip": "10.0.0.2", "dst_port": 443}, 30),
    ]
    groups = CorrelationEngine(window_seconds=300).correlate(events)
    assert len(groups) == 2


def test_correlation_requires_allowed_key():
    events = [make_event("a", {"severity": "high"}, 0), make_event("b", {"severity": "high"}, 30)]
    groups = CorrelationEngine(window_seconds=300).correlate(events)
    assert len(groups) == 2


def test_correlation_ignores_complex_observable_values():
    events = [
        make_event("a", {"src_ip": "10.0.0.1", "labels": ["one", "two"]}, 0),
        make_event("b", {"src_ip": "10.0.0.1", "labels": ["different"]}, 30),
    ]
    groups = CorrelationEngine(window_seconds=300).correlate(events)
    assert [[event.event_id for event in group] for group in groups] == [["a", "b"]]


def test_correlation_multi_key_event_matches_any_allowed_key():
    events = [
        make_event("a", {"src_ip": "10.0.0.1", "uid": "C-1"}, 0),
        make_event("b", {"src_ip": "10.0.0.9", "uid": "C-1"}, 20),
    ]
    groups = CorrelationEngine(window_seconds=300).correlate(events)
    assert [[event.event_id for event in group] for group in groups] == [["a", "b"]]


def test_correlation_candidate_groups_are_deterministic():
    events = [
        make_event("a", {"src_ip": "10.0.0.1", "uid": "one"}, 0),
        make_event("b", {"src_ip": "10.0.0.1", "uid": "two"}, 10),
        make_event("c", {"src_ip": "10.0.0.1", "uid": "two"}, 20),
    ]
    groups = CorrelationEngine(window_seconds=300).correlate(events)
    assert [[event.event_id for event in group] for group in groups] == [["a", "b", "c"]]


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
    assert case.decision is None
    assert case.action is None
    assert case.human_authority is None
