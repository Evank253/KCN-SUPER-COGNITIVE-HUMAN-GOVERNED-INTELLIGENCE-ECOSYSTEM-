"""Deterministic confidence normalization for Security Fabric events.

Vendor platforms do not share a scale:
- STIX 2.1 `confidence` is 0-100
- OpenCTI `confidence` and `x_opencti_score` are typically 0-100
- MISP attributes sometimes carry 0-100 confidence
- KCN SecurityEvent.confidence is a closed unit interval [0.0, 1.0]

This module converts vendor values onto that unit interval. It does not
invent confidence, and it does not treat MISP threat_level_id as confidence.
"""

from __future__ import annotations

from typing import Any


class ConfidenceError(ValueError):
    """Raised when a vendor confidence value cannot be normalized safely."""


def normalize_confidence(value: Any) -> float | None:
    """Return a unit-interval confidence, or None when the vendor omitted it.

    Rules:
    - None / empty string -> None
    - bool is rejected (bool is an int subclass and would silently become 0 or 1)
    - 0.0 <= n <= 1.0 -> already normalized
    - 1.0 < n <= 100.0 -> percent scale, divided by 100
    - anything else -> ConfidenceError
    """
    if value is None:
        return None
    if isinstance(value, bool):
        raise ConfidenceError("boolean is not a valid confidence value")
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            value = float(text)
        except ValueError as exc:
            raise ConfidenceError(f"confidence is not numeric: {value!r}") from exc
    if isinstance(value, int):
        value = float(value)
    if not isinstance(value, float):
        raise ConfidenceError(f"unsupported confidence type: {type(value).__name__}")
    if value != value:  # NaN
        raise ConfidenceError("confidence is not a finite number")
    if value < 0.0:
        raise ConfidenceError(f"confidence below 0: {value}")
    if value <= 1.0:
        return value
    if value <= 100.0:
        return round(value / 100.0, 6)
    raise ConfidenceError(f"confidence above 100: {value}")


def first_confidence(*values: Any) -> float | None:
    """Return the first present, normalizable confidence from vendor fields."""
    for value in values:
        if value is None or value == "":
            continue
        return normalize_confidence(value)
    return None
