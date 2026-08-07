"""Simple in-memory login rate limit + temporary lockout for the twin."""

from __future__ import annotations

import threading
import time
from collections import defaultdict

from app.config import settings

_lock = threading.Lock()
# key -> list of failure timestamps
_failures: dict[str, list[float]] = defaultdict(list)
# key -> lockout_until timestamp
_lockouts: dict[str, float] = {}


def _key(username: str, client: str) -> str:
    return f"{username.lower()}|{client}"


def is_locked(username: str, client: str) -> tuple[bool, float]:
    """Return (locked, seconds_remaining)."""
    k = _key(username, client)
    now = time.time()
    with _lock:
        until = _lockouts.get(k, 0.0)
        if until > now:
            return True, round(until - now, 1)
        if until and until <= now:
            _lockouts.pop(k, None)
            _failures.pop(k, None)
        return False, 0.0


def record_failure(username: str, client: str) -> tuple[bool, float]:
    """
    Record a failed login. Returns (now_locked, lockout_seconds_or_0).
    """
    k = _key(username, client)
    now = time.time()
    window = settings.login_window_seconds
    max_fail = settings.login_max_failures
    lock_secs = settings.login_lockout_seconds

    with _lock:
        # prune old failures
        _failures[k] = [t for t in _failures[k] if now - t < window]
        _failures[k].append(now)
        if len(_failures[k]) >= max_fail:
            _lockouts[k] = now + lock_secs
            _failures[k].clear()
            return True, float(lock_secs)
        return False, 0.0


def record_success(username: str, client: str) -> None:
    k = _key(username, client)
    with _lock:
        _failures.pop(k, None)
        _lockouts.pop(k, None)
