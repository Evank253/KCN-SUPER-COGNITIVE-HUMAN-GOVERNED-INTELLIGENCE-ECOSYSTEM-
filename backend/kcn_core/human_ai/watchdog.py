"""Human-AI watchdog — safety interlock. Resume is human-authority only."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any


class WatchdogState(str, Enum):
    RUNNING = "RUNNING"
    KILLED = "KILLED"
    FROZEN = "FROZEN"


class HumanAIWatchdog:
    """Dual cyber watchdog + killswitch. Agents cannot resume after kill."""

    def __init__(self) -> None:
        self.state = WatchdogState.RUNNING
        self.reason: str | None = None
        self.updated_at = datetime.now(timezone.utc).isoformat()
        self._events: list[dict[str, Any]] = []

    def _audit(self, event: str, **extra: Any) -> None:
        rec = {
            "event": event,
            "state": self.state.value,
            "ts": datetime.now(timezone.utc).isoformat(),
            **extra,
        }
        self._events.append(rec)

    def status(self) -> dict[str, Any]:
        return {
            "state": self.state.value,
            "reason": self.reason,
            "updated_at": self.updated_at,
            "agent_resume_forbidden": True,
            "principle": "Humans govern. Agents execute. No self-change without human acceptance.",
        }

    def kill(self, reason: str = "safety", actor: str = "system") -> dict[str, Any]:
        self.state = WatchdogState.KILLED
        self.reason = reason
        self.updated_at = datetime.now(timezone.utc).isoformat()
        self._audit("kill", reason=reason, actor=actor)
        return self.status()

    def freeze(self, reason: str = "freeze", actor: str = "system") -> dict[str, Any]:
        self.state = WatchdogState.FROZEN
        self.reason = reason
        self.updated_at = datetime.now(timezone.utc).isoformat()
        self._audit("freeze", reason=reason, actor=actor)
        return self.status()

    def resume(self, actor_role: str, actor_id: str = "") -> dict[str, Any]:
        """Resume only for human-authority roles. Agents always denied."""
        role = (actor_role or "").lower()
        if role in {"agent", "ai", "service", "system_agent"}:
            self._audit("resume_denied", actor_role=role, actor_id=actor_id, http_hint=403)
            return {
                "allowed": False,
                "http_status": 403,
                "reason": "not_human_authority",
                "state": self.state.value,
                "message": "Agent cannot resume watchdog. Human authority required.",
            }
        if role not in {"human", "governance", "security_officer", "admin", "human_operator"}:
            self._audit("resume_denied", actor_role=role, actor_id=actor_id, http_hint=403)
            return {
                "allowed": False,
                "http_status": 403,
                "reason": "insufficient_role",
                "state": self.state.value,
            }
        self.state = WatchdogState.RUNNING
        self.reason = None
        self.updated_at = datetime.now(timezone.utc).isoformat()
        self._audit("resume_allowed", actor_role=role, actor_id=actor_id)
        return {"allowed": True, "http_status": 200, **self.status()}


human_ai_governance = HumanAIWatchdog()
