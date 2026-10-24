"""Deterministic correlation foundation.

Correlation only groups canonical observations. It does not infer threat
identity, authorize actions, or create security cases.
"""

from collections import defaultdict
from collections.abc import Iterable
from datetime import datetime, timedelta, timezone
from typing import Any, ClassVar

from app.security_fabric.models import SecurityEvent


class CorrelationEngine:
    """Conservative observable-overlap correlation with an origin window."""

    ALLOWED_JOIN_KEYS: ClassVar[frozenset[str]] = frozenset({
        "src_ip", "dst_ip", "ip", "domain", "url", "hash", "uid",
        "session_id", "agent_id", "client_id", "flow_id", "stix_id",
        "event_uuid", "container_id",
        "hash_md5", "hash_sha1", "hash_sha256", "hash_sha512", "email",
    })
    SCALAR_TYPES: ClassVar[tuple[type[Any], ...]] = (str, int, float, bool)

    def __init__(self, window_seconds: int = 300) -> None:
        if window_seconds < 0:
            raise ValueError("window_seconds must be non-negative")
        self.window = timedelta(seconds=window_seconds)

    @classmethod
    def _keys(cls, event: SecurityEvent) -> set[tuple[str, str]]:
        keys: set[tuple[str, str]] = set()
        for key, value in event.observable.items():
            if key not in cls.ALLOWED_JOIN_KEYS or value is None:
                continue
            if not isinstance(value, cls.SCALAR_TYPES):
                continue
            keys.add((str(key), str(value)))
        return keys

    def correlate(self, events: Iterable[SecurityEvent]) -> list[list[SecurityEvent]]:
        groups: list[list[SecurityEvent]] = []
        indexed: dict[tuple[str, str], list[int]] = defaultdict(list)
        ordered = sorted(events, key=lambda event: event.timestamp)

        for event in ordered:
            candidates: set[int] = set()
            for key in self._keys(event):
                candidates.update(indexed.get(key, []))

            selected = next(
                (idx for idx in sorted(candidates) if self._compatible(groups[idx][0], event)),
                None,
            )
            if selected is None:
                groups.append([event])
                group_id = len(groups) - 1
            else:
                groups[selected].append(event)
                group_id = selected

            for key in self._keys(event):
                indexed[key].append(group_id)
        return groups

    def _compatible(self, left: SecurityEvent, right: SecurityEvent) -> bool:
        left_ts = self._utc(left.timestamp)
        right_ts = self._utc(right.timestamp)
        return abs(right_ts - left_ts) <= self.window

    @staticmethod
    def _utc(value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
