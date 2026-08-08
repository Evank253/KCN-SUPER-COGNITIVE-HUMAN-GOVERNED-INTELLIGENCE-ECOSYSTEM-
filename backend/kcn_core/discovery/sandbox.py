"""Sealed Discovery sandbox — transparent exploration; promotion needs human."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any


class DiscoverySandbox:
    def __init__(self) -> None:
        self._items: dict[str, dict[str, Any]] = {}

    def propose(self, title: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        item_id = f"disc-{uuid.uuid4().hex[:12]}"
        rec = {
            "id": item_id,
            "title": title,
            "payload": payload or {},
            "status": "sandboxed",
            "promoted": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._items[item_id] = rec
        return rec

    def list_items(self) -> list[dict[str, Any]]:
        return list(self._items.values())

    def decide_promotion(
        self, item_id: str, approve: bool, actor_role: str
    ) -> dict[str, Any]:
        """Promotion decision is human-authority only (agent → 403)."""
        if (actor_role or "").lower() in {"agent", "ai", "service", "system_agent"}:
            return {
                "allowed": False,
                "http_status": 403,
                "reason": "not_human_authority",
                "message": "Agents cannot promote discovery items.",
            }
        item = self._items.get(item_id)
        if not item:
            return {"allowed": False, "http_status": 404, "reason": "not_found"}
        item["status"] = "promoted" if approve else "rejected"
        item["promoted"] = bool(approve)
        item["decided_at"] = datetime.now(timezone.utc).isoformat()
        return {"allowed": True, "http_status": 200, "item": item}


sandbox = DiscoverySandbox()
