"""Judgment bridge — recommendations only; authority stays human."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class JudgmentBridge:
    def recommend(self, question: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        return {
            "type": "recommendation",
            "question": question,
            "context": context or {},
            "binding": False,
            "requires_human_acceptance": True,
            "ts": datetime.now(timezone.utc).isoformat(),
            "note": "Judgment bridge never auto-executes privileged actions.",
        }


judgment_bridge = JudgmentBridge()
