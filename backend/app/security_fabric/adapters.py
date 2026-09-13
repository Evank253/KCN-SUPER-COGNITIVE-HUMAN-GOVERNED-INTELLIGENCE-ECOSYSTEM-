"""Vendor boundaries for KCN Security Fabric.

Adapters translate vendor telemetry into the canonical SecurityEvent. They do
not authorize actions and they do not assign KCN trust merely because an
engine emitted an alert.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any, ClassVar

from app.security_fabric.models import SecurityEvent


class AdapterError(ValueError):
    """Raised when a vendor event cannot be safely normalized."""


class AdapterResult:
    def __init__(self, event: SecurityEvent, raw_hash: str) -> None:
        self.event = event
        self.raw_hash = raw_hash


class Adapter(ABC):
    source: ClassVar[str]
    engine: ClassVar[str]

    @classmethod
    def _hash_raw(cls, raw: dict[str, Any]) -> str:
        import json

        payload = json.dumps(raw, sort_keys=True, separators=(",", ":"), default=str)
        return sha256(payload.encode("utf-8")).hexdigest()

    @classmethod
    def _timestamp(cls, raw: dict[str, Any]) -> datetime:
        value = raw.get("timestamp") or raw.get("ts")
        if isinstance(value, datetime):
            return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(value, tz=timezone.utc)
        if isinstance(value, str):
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        return datetime.now(timezone.utc)

    @classmethod
    def _base(cls, raw: dict[str, Any], event_type: str, observable: dict[str, Any], **kwargs: Any) -> SecurityEvent:
        event_id = str(raw.get("event_id") or raw.get("uid") or raw.get("id") or sha256(repr(sorted(raw.items())).encode()).hexdigest()[:24])
        return SecurityEvent(
            event_id=event_id,
            source=cls.source,
            sensor_id=str(raw.get("sensor_id") or raw.get("sensor") or cls.source),
            timestamp=cls._timestamp(raw),
            event_type=event_type,
            observable=observable,
            provenance={"adapter": cls.__name__, "engine": cls.engine, "raw_event": True},
            **kwargs,
        )

    @classmethod
    @abstractmethod
    def adapt(cls, raw: dict[str, Any]) -> AdapterResult:
        raise NotImplementedError


def _require(raw: dict[str, Any], key: str) -> Any:
    if key not in raw:
        raise AdapterError(f"missing required field: {key}")
    return raw[key]


class ZeekAdapter(Adapter):
    source = "zeek"
    engine = "Zeek"

    @classmethod
    def adapt(cls, raw: dict[str, Any]) -> AdapterResult:
        event = cls._base(raw, str(raw.get("event_type") or raw.get("service") or "network"), {
            "src_ip": raw.get("id.orig_h"), "src_port": raw.get("id.orig_p"),
            "dst_ip": raw.get("id.resp_h"), "dst_port": raw.get("id.resp_p"),
            "uid": raw.get("uid"),
        }, detection=raw.get("notice_type"), confidence=raw.get("confidence"))
        return AdapterResult(event, cls._hash_raw(raw))


class SuricataAdapter(Adapter):
    source = "suricata"
    engine = "Suricata"

    @classmethod
    def adapt(cls, raw: dict[str, Any]) -> AdapterResult:
        alert = raw.get("alert") or {}
        event = cls._base(raw, str(raw.get("event_type") or "alert"), {
            "src_ip": raw.get("src_ip"), "src_port": raw.get("src_port"),
            "dst_ip": raw.get("dest_ip"), "dst_port": raw.get("dest_port"),
            "signature_id": alert.get("signature_id"),
        }, detection=alert.get("signature"), threat=alert.get("category"), confidence=raw.get("confidence"))
        return AdapterResult(event, cls._hash_raw(raw))


class WazuhAdapter(Adapter):
    source = "wazuh"
    engine = "Wazuh"

    @classmethod
    def adapt(cls, raw: dict[str, Any]) -> AdapterResult:
        rule = raw.get("rule") or {}
        agent = raw.get("agent") or {}
        event = cls._base(raw, str(raw.get("event_type") or "endpoint_alert"), {
            "agent_id": agent.get("id"), "agent_name": agent.get("name"),
            "rule_id": rule.get("id"), "level": rule.get("level"),
        }, agent_id=agent.get("id"), detection=rule.get("description"), confidence=raw.get("confidence"))
        return AdapterResult(event, cls._hash_raw(raw))


class VelociraptorAdapter(Adapter):
    source = "velociraptor"
    engine = "Velociraptor"

    @classmethod
    def adapt(cls, raw: dict[str, Any]) -> AdapterResult:
        event = cls._base(raw, str(raw.get("event_type") or "endpoint_artifact"), {
            "client_id": raw.get("client_id"), "artifact_name": raw.get("artifact_name"),
            "flow_id": raw.get("flow_id"),
        }, detection=raw.get("detection"), artifact=raw.get("artifact"))
        return AdapterResult(event, cls._hash_raw(raw))


class ArkimeAdapter(Adapter):
    source = "arkime"
    engine = "Arkime"

    @classmethod
    def adapt(cls, raw: dict[str, Any]) -> AdapterResult:
        event = cls._base(raw, "session", {
            "src_ip": raw.get("source.ip"), "src_port": raw.get("source.port"),
            "dst_ip": raw.get("destination.ip"), "dst_port": raw.get("destination.port"),
            "session_id": raw.get("sessionId") or raw.get("session_id"),
        }, detection=raw.get("detection"))
        return AdapterResult(event, cls._hash_raw(raw))


class OpenCTIAdapter(Adapter):
    source = "opencti"
    engine = "OpenCTI"

    @classmethod
    def adapt(cls, raw: dict[str, Any]) -> AdapterResult:
        event = cls._base(raw, "threat_intelligence", {
            "stix_id": raw.get("id") or raw.get("stix_id"),
            "entity_type": raw.get("entity_type"), "labels": raw.get("labels", []),
        }, threat=raw.get("threat"), confidence=raw.get("confidence"), entity=raw.get("entity") or {})
        return AdapterResult(event, cls._hash_raw(raw))


class MISPAdapter(Adapter):
    source = "misp"
    engine = "MISP"

    @classmethod
    def adapt(cls, raw: dict[str, Any]) -> AdapterResult:
        event = cls._base(raw, "threat_intelligence", {
            "event_uuid": raw.get("uuid") or raw.get("event_uuid"),
            "attribute_type": raw.get("type"), "value": raw.get("value"),
        }, threat=raw.get("threat"), confidence=raw.get("confidence"))
        return AdapterResult(event, cls._hash_raw(raw))


class SigmaAdapter(Adapter):
    source = "sigma"
    engine = "Sigma"

    @classmethod
    def adapt(cls, raw: dict[str, Any]) -> AdapterResult:
        event = cls._base(raw, "detection_rule_match", {
            "rule_id": raw.get("rule_id"), "rule_name": raw.get("rule_name"),
            "backend": raw.get("backend"),
        }, detection=raw.get("detection") or raw.get("rule_name"), confidence=raw.get("confidence"))
        return AdapterResult(event, cls._hash_raw(raw))


class YaraAdapter(Adapter):
    source = "yara"
    engine = "YARA/YARA-X"

    @classmethod
    def adapt(cls, raw: dict[str, Any]) -> AdapterResult:
        event = cls._base(raw, "artifact_match", {
            "rule": raw.get("rule"), "target": raw.get("target"),
            "namespace": raw.get("namespace"),
        }, detection=raw.get("rule"), artifact=raw.get("artifact"))
        return AdapterResult(event, cls._hash_raw(raw))


class FalcoAdapter(Adapter):
    source = "falco"
    engine = "Falco"

    @classmethod
    def adapt(cls, raw: dict[str, Any]) -> AdapterResult:
        event = cls._base(raw, "runtime_alert", {
            "container_id": raw.get("container.id"), "pod": raw.get("k8s.pod.name"),
            "namespace": raw.get("k8s.ns.name"), "process": raw.get("proc.name"),
        }, detection=raw.get("rule") or raw.get("output"), confidence=raw.get("confidence"))
        return AdapterResult(event, cls._hash_raw(raw))


ADAPTERS: dict[str, type[Adapter]] = {
    cls.source: cls
    for cls in (
        ZeekAdapter, SuricataAdapter, WazuhAdapter, VelociraptorAdapter,
        ArkimeAdapter, OpenCTIAdapter, MISPAdapter, SigmaAdapter,
        YaraAdapter, FalcoAdapter,
    )
}
