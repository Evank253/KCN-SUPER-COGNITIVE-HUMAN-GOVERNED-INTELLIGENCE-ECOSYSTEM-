"""Deterministic correlation foundation.

This first implementation deliberately uses conservative observable overlap;
it does not infer threat identity merely because events are temporally close.
"""

from collections import defaultdict
from collections.abc import Iterable
from datetime import timedelta

from app.security_fabric.models import SecurityEvent


class CorrelationEngine:
    def __init__(self, window_seconds: int = 300) -> None:
        self.window = timedelta(seconds=window_seconds)

    @staticmethod
    def _keys(event: SecurityEvent) -> set[tuple[str, str]]:
        return {
            (str(key), str(value))
            for key, value in event.observable.items()
            if value is not None
        }

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
        return abs(right.timestamp - left.timestamp) <= self.window
