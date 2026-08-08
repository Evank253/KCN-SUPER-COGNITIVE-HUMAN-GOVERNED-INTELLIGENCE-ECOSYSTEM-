"""Human-AI Twin — ecosystem counterpart (not a chat companion)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class HumanAITwin:
    """Tracks human–system pairing state for the ecosystem, not conversational UI."""

    def __init__(self) -> None:
        self.bound_human_id: str | None = None
        self.mode = "observe"
        self.created_at = datetime.now(timezone.utc).isoformat()

    def status(self) -> dict[str, Any]:
        return {
            "component": "human_ai_twin",
            "bound_human_id": self.bound_human_id,
            "mode": self.mode,
            "authority": "human_only_for_binding_changes",
            "created_at": self.created_at,
        }

    def bind(self, human_id: str, actor_role: str) -> dict[str, Any]:
        if (actor_role or "").lower() in {"agent", "ai", "service"}:
            return {"allowed": False, "http_status": 403, "reason": "not_human_authority"}
        self.bound_human_id = human_id
        return {"allowed": True, **self.status()}


twin = HumanAITwin()
