"""Persistent, append-only approval state for Security Fabric governance."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Any


class GovernanceStore:
    """Small JSONL-backed store; each state transition is an immutable record."""

    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path or os.getenv("KCN_GOVERNANCE_STORE", "data/governance_approvals.jsonl"))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = RLock()

    def _records(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        records: list[dict[str, Any]] = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    records.append(json.loads(line))
        return records

    def _append(self, record: dict[str, Any]) -> None:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")

    def create(self, approval_id: str, case_id: str | None, action_type: str, description: str, data: dict | None) -> dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        record = {
            "approval_id": approval_id,
            "case_id": case_id,
            "action_type": action_type,
            "description": description,
            "data": data or {},
            "status": "pending",
            "created_at": now,
            "updated_at": now,
            "human_authority": None,
        }
        with self._lock:
            self._append({"type": "approval_created", **record})
        return record

    def get(self, approval_id: str) -> dict[str, Any] | None:
        with self._lock:
            latest: dict[str, Any] | None = None
            for record in self._records():
                if record.get("approval_id") == approval_id:
                    latest = {k: v for k, v in record.items() if k != "type"}
            return latest

    def decide(self, approval_id: str, status: str, human_authority: str) -> dict[str, Any] | None:
        if status not in {"approved", "rejected"}:
            raise ValueError("status must be approved or rejected")
        if not human_authority.strip():
            raise ValueError("human_authority is required")
        with self._lock:
            current = self.get(approval_id)
            if current is None:
                return None
            if current["status"] != "pending":
                raise ValueError("approval is already decided")
            updated = {
                **current,
                "status": status,
                "human_authority": human_authority,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            self._append({"type": "approval_decision", **updated})
            return updated

    def can_authorize(self, approval_id: str, case_id: str) -> bool:
        record = self.get(approval_id)
        return bool(
            record
            and record.get("case_id") == case_id
            and record.get("status") == "approved"
            and record.get("human_authority")
        )
