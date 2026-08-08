"""Self-modification lock — no self-change without human acceptance."""

from __future__ import annotations

from typing import Any

from backend.governance.engine import governance


class GovernanceLock:
    def evaluate_self_mod(self, action: str, intent: str = "") -> dict[str, Any]:
        return governance.evaluate(action, intent)

    def agent_may_accept(self) -> bool:
        return False


governance_lock = GovernanceLock()
