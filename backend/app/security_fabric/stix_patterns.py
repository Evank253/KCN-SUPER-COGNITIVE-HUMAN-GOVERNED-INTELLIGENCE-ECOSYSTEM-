"""Conservative STIX 2.1 Indicator pattern extraction.

This is not a STIX patterning engine. It does not evaluate AND/OR/FOLLOWEDBY,
WITHIN, START/STOP, object references, or set comparisons. It extracts
equality atoms from a `pattern_type=stix` observation so adapters can copy
SCO values onto canonical observable keys.

Supported atom shape:
    [ipv4-addr:value = '198.51.100.1']
    [file:hashes.'SHA-256' = 'abc...']
    [domain-name:value = 'evil.example' AND url:value = 'https://evil.example/a']

Unsupported patterns are retained as raw text and produce no join keys.
"""

from __future__ import annotations

import re
from typing import Any

from app.security_fabric.confidence import first_confidence


_ATOM = re.compile(
    r"(?P<object_type>[a-z0-9-]+):"
    r"(?P<property>[A-Za-z0-9_.-]+(?:\.'[^']+'|\.\"[^\"]+\")*)"
    r"\s*=\s*"
    r"(?P<value>'([^'\\]|\\.)*'|\"([^\"\\]|\\.)*\"|[0-9]+(?:\.[0-9]+)?)",
    re.IGNORECASE,
)

_HASH_PROPERTY = re.compile(
    r"hashes\.(?:'([^']+)'|\"([^\"]+)\"|([A-Za-z0-9-]+))",
    re.IGNORECASE,
)

_OBJECT_KEY = {
    "ipv4-addr": "ip",
    "ipv6-addr": "ip",
    "mac-addr": "mac",
    "domain-name": "domain",
    "hostname": "domain",
    "url": "url",
    "email-addr": "email",
    "directory": "path",
    "windows-registry-key": "registry_key",
    "mutex": "mutex",
    "user-account": "user",
    "software": "software",
    "autonomous-system": "asn",
}

_HASH_KEY = {
    "md5": "hash_md5",
    "sha1": "hash_sha1",
    "sha-1": "hash_sha1",
    "sha256": "hash_sha256",
    "sha-256": "hash_sha256",
    "sha512": "hash_sha512",
    "sha-512": "hash_sha512",
}


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        inner = value[1:-1]
        return inner.replace(r"\'", "'").replace(r"\"", '"').replace(r"\\", "\\")
    return value


def parse_stix_pattern(pattern: str | None) -> list[dict[str, str]]:
    """Extract equality atoms from a STIX 2.1 pattern string."""
    if not pattern or not isinstance(pattern, str):
        return []
    atoms: list[dict[str, str]] = []
    for match in _ATOM.finditer(pattern):
        atoms.append(
            {
                "object_type": match.group("object_type").lower(),
                "property": match.group("property"),
                "value": _unquote(match.group("value")),
            }
        )
    return atoms


def observables_from_stix_pattern(pattern: str | None) -> dict[str, Any]:
    """Flatten extracted atoms onto canonical observable keys.

    Multiple values for the same key keep the first value. Extra values are
    not turned into lists so correlation will not stringify a list join key.
    """
    observable: dict[str, Any] = {}
    for atom in parse_stix_pattern(pattern):
        key = _observable_key(atom["object_type"], atom["property"])
        if key and key not in observable:
            observable[key] = atom["value"]
    return observable


def _observable_key(object_type: str, property_name: str) -> str | None:
    if object_type == "file":
        hash_match = _HASH_PROPERTY.search(property_name)
        if hash_match:
            algorithm = next(group for group in hash_match.groups() if group).lower()
            return _HASH_KEY.get(algorithm)
        if property_name.lower() == "name":
            return "filename"
        return None
    if object_type == "network-traffic":
        lowered = property_name.lower()
        if lowered in {"src_port", "src-port"}:
            return "src_port"
        if lowered in {"dst_port", "dst-port"}:
            return "dst_port"
        return None
    if property_name.split(".")[0].lower() != "value" and object_type in {
        "ipv4-addr",
        "ipv6-addr",
        "domain-name",
        "url",
        "email-addr",
        "mac-addr",
    }:
        if "value" not in property_name.lower():
            return None
    return _OBJECT_KEY.get(object_type)


def indicator_fields(raw: dict[str, Any]) -> dict[str, Any]:
    """Read STIX 2.1 Indicator / OpenCTI Indicator fields without trusting them.

    Does not set threat. A pattern match is not a KCN detection by itself.
    """
    pattern = raw.get("pattern")
    pattern_type = str(raw.get("pattern_type") or raw.get("patternType") or "").lower()
    observable: dict[str, Any] = {}
    if pattern_type in {"", "stix"}:
        observable.update(observables_from_stix_pattern(pattern if isinstance(pattern, str) else None))

    stix_id = raw.get("id") or raw.get("standard_id") or raw.get("stix_id")
    entity_type = raw.get("type") or raw.get("entity_type") or raw.get("entityType")
    if stix_id:
        observable["stix_id"] = stix_id
    if entity_type:
        observable["entity_type"] = str(entity_type)

    labels = raw.get("labels") or raw.get("indicator_types") or raw.get("indicatorTypes") or []
    entity = {
        "stix_id": stix_id,
        "entity_type": entity_type,
        "name": raw.get("name"),
        "pattern_type": raw.get("pattern_type") or raw.get("patternType") or "stix",
        "spec_version": raw.get("spec_version") or raw.get("specVersion"),
    }
    if labels:
        entity["labels"] = labels
    if isinstance(pattern, str):
        entity["pattern"] = pattern

    return {
        "event_type": "threat_intelligence",
        "observable": {key: value for key, value in observable.items() if value not in (None, "")},
        "entity": {key: value for key, value in entity.items() if value not in (None, "", [])},
        "detection": raw.get("name") or raw.get("detection"),
        "confidence": first_confidence(
            raw.get("confidence"),
            raw.get("x_opencti_score"),
            raw.get("x_opencti_confidence"),
        ),
        "timestamp_hint": raw.get("valid_from") or raw.get("validFrom") or raw.get("created") or raw.get("modified"),
    }
