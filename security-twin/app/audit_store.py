"""
Append-only audit store for the KCN Security Twin.

Every record is marked as a twin test log. Nothing here is production evidence.
"""

from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

LOG_DIR = Path("/logs")
LOG_FILE = LOG_DIR / "twin-audit.jsonl"

_lock = threading.Lock()
_events: list[dict[str, Any]] = []
_MAX_MEMORY = 10_000


def _ensure_log_dir() -> None:
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
    except OSError:
        # Fall back to local dir if /logs is not writable (e.g. bare run)
        pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def record(event_type: str, **fields: Any) -> dict[str, Any]:
    """Append a structured audit event. Returns the event dict."""
    event: dict[str, Any] = {
        "ts": _now(),
        "event": event_type,
        "twin": True,
        "notice": "TWIN TEST LOG — NOT PRODUCTION",
        **fields,
    }
    line = json.dumps(event, default=str) + "\n"

    with _lock:
        _events.append(event)
        if len(_events) > _MAX_MEMORY:
            del _events[: len(_events) - _MAX_MEMORY]

        _ensure_log_dir()
        target = LOG_FILE if LOG_DIR.exists() else Path("twin-audit.jsonl")
        try:
            with target.open("a", encoding="utf-8") as f:
                f.write(line)
        except OSError:
            pass  # still keep in-memory copy

    return event


def get_events(limit: int | None = None) -> list[dict[str, Any]]:
    with _lock:
        if limit is None:
            return list(_events)
        return list(_events[-limit:])


def summary() -> dict[str, Any]:
    with _lock:
        total = len(_events)
        by_status: dict[str, int] = {}
        by_path: dict[str, int] = {}
        auth_fail = 0
        auth_ok = 0
        canary = 0
        for e in _events:
            st = str(e.get("status", e.get("event", "unknown")))
            by_status[st] = by_status.get(st, 0) + 1
            path = str(e.get("path", ""))
            if path:
                by_path[path] = by_path.get(path, 0) + 1
            if e.get("event") == "auth_failure":
                auth_fail += 1
            if e.get("event") == "auth_success":
                auth_ok += 1
            if e.get("event") == "canary_hit":
                canary += 1
        return {
            "total_events": total,
            "auth_success": auth_ok,
            "auth_failure": auth_fail,
            "canary_hits": canary,
            "by_status": by_status,
            "top_paths": dict(sorted(by_path.items(), key=lambda x: -x[1])[:20]),
            "twin": True,
            "notice": "TWIN TEST LOG — NOT PRODUCTION",
        }


def clear() -> None:
    """Clear in-memory events (file is left intact for permanence)."""
    with _lock:
        _events.clear()
