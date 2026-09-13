"""MISP JSON Event / Attribute mapping for Security Fabric adapters.

Handles the common MISP REST shapes:
- wrapped Event: {"Event": {...}}
- Event document: {"uuid", "info", "Attribute": [...]}
- single Attribute: {"uuid", "type", "value", "category"}

This is not a MISP correlation engine. Composite MISP types such as
`filename|sha256` are split into scalar observable keys. threat_level_id is
recorded on the entity and is never treated as confidence.
"""

from __future__ import annotations

from typing import Any

from app.security_fabric.confidence import first_confidence


_TYPE_KEY = {
    "ip-src": "src_ip",
    "ip-dst": "dst_ip",
    "ip-src|port": "src_ip",
    "ip-dst|port": "dst_ip",
    "ip": "ip",
    "domain": "domain",
    "hostname": "domain",
    "domain|ip": "domain",
    "url": "url",
    "uri": "url",
    "md5": "hash_md5",
    "sha1": "hash_sha1",
    "sha256": "hash_sha256",
    "sha512": "hash_sha512",
    "filename": "filename",
    "filename|md5": "filename",
    "filename|sha1": "filename",
    "filename|sha256": "filename",
    "email-src": "email",
    "email-dst": "email",
    "email": "email",
    "mutex": "mutex",
    "regkey": "registry_key",
    "target-user": "user",
    "whois-registrant-email": "email",
}


def unwrap_event(raw: dict[str, Any]) -> dict[str, Any]:
    event = raw.get("Event")
    if isinstance(event, dict):
        return event
    return raw


def is_misp_event(raw: dict[str, Any]) -> bool:
    event = unwrap_event(raw)
    return isinstance(event.get("Attribute"), list) or isinstance(event.get("attributes"), list)


def is_misp_attribute(raw: dict[str, Any]) -> bool:
    return "type" in raw and "value" in raw and "Attribute" not in raw and "Event" not in raw


def _attributes(event: dict[str, Any]) -> list[dict[str, Any]]:
    attributes = event.get("Attribute") or event.get("attributes") or []
    if isinstance(attributes, dict):
        return [attributes]
    return [item for item in attributes if isinstance(item, dict)]


def _split_composite(attr_type: str, value: str) -> dict[str, Any]:
    observable: dict[str, Any] = {}
    if "|" not in attr_type:
        key = _TYPE_KEY.get(attr_type)
        if key:
            observable[key] = value
        return observable

    left_type, right_type = attr_type.split("|", 1)
    if "|" in value:
        left_value, right_value = value.split("|", 1)
    else:
        left_value, right_value = value, None
    left_key = _TYPE_KEY.get(left_type) or _TYPE_KEY.get(attr_type)
    right_key = _TYPE_KEY.get(right_type)
    if left_key and left_value:
        observable[left_key] = left_value
    if right_key and right_value:
        observable[right_key] = right_value
    if attr_type.endswith("|port") and right_value:
        port_key = "src_port" if attr_type.startswith("ip-src") else "dst_port"
        observable[port_key] = right_value
    return observable


def observables_from_attribute(attribute: dict[str, Any]) -> dict[str, Any]:
    attr_type = str(attribute.get("type") or "")
    value = attribute.get("value")
    if value is None:
        return {}
    return _split_composite(attr_type, str(value))


def event_fields(raw: dict[str, Any]) -> dict[str, Any]:
    """Map a MISP Event or Attribute onto adapter fields."""
    if is_misp_attribute(raw):
        observable = observables_from_attribute(raw)
        if raw.get("uuid"):
            observable["event_uuid"] = raw.get("uuid")
        if raw.get("type"):
            observable["attribute_type"] = raw.get("type")
        if "value" in raw and "value" not in observable:
            observable["value"] = raw.get("value")
        return {
            "event_id": raw.get("uuid") or raw.get("event_uuid") or raw.get("id"),
            "event_type": "threat_intelligence",
            "observable": observable,
            "entity": {
                "attribute_uuid": raw.get("uuid"),
                "category": raw.get("category"),
                "to_ids": raw.get("to_ids"),
            },
            "detection": raw.get("comment") or raw.get("detection"),
            "confidence": first_confidence(raw.get("confidence")),
            "timestamp_hint": raw.get("timestamp"),
        }

    event = unwrap_event(raw)
    observable: dict[str, Any] = {}
    if event.get("uuid"):
        observable["event_uuid"] = event.get("uuid")
    for attribute in _attributes(event):
        extracted = observables_from_attribute(attribute)
        for key, value in extracted.items():
            if key not in observable and value not in (None, ""):
                observable[key] = value

    org_block = event.get("Orgc") or event.get("orgc")
    entity = {
        "event_uuid": event.get("uuid"),
        "info": event.get("info"),
        "threat_level_id": event.get("threat_level_id"),
        "analysis": event.get("analysis"),
        "org": org_block.get("name") if isinstance(org_block, dict) else None,
    }
    tags = event.get("Tag") or event.get("tags") or []
    if tags:
        entity["tags"] = [
            tag.get("name") if isinstance(tag, dict) else tag
            for tag in tags
        ]

    return {
        "event_id": event.get("uuid") or event.get("id"),
        "event_type": "threat_intelligence",
        "observable": {key: value for key, value in observable.items() if value not in (None, "")},
        "entity": {key: value for key, value in entity.items() if value not in (None, "", [])},
        "detection": event.get("info") or event.get("detection"),
        "confidence": first_confidence(event.get("confidence"), raw.get("confidence")),
        "timestamp_hint": event.get("timestamp") or event.get("date") or event.get("publish_timestamp"),
    }
