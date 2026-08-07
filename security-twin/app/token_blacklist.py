"""In-memory token blacklist (jti-based) for logout revocation."""

from __future__ import annotations

import threading
import time

_lock = threading.Lock()
# jti -> expires_at (unix)
_revoked: dict[str, float] = {}


def revoke(jti: str, exp: float | None = None) -> None:
    if not jti:
        return
    with _lock:
        _revoked[jti] = exp if exp else time.time() + 86400


def is_revoked(jti: str | None) -> bool:
    if not jti:
        return False
    now = time.time()
    with _lock:
        exp = _revoked.get(jti)
        if exp is None:
            return False
        if exp < now:
            _revoked.pop(jti, None)
            return False
        return True


def purge_expired() -> int:
    now = time.time()
    with _lock:
        dead = [j for j, e in _revoked.items() if e < now]
        for j in dead:
            del _revoked[j]
        return len(dead)
