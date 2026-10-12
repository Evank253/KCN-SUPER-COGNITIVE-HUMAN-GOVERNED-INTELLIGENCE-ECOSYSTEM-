"""Memory coordination across agents and subsystems."""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
import uuid

class MemoryEntry(BaseModel):
    entry_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    owner_id: str
    scope: str
    key: str
    value: Dict
    importance: float = 0.5
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)

class MemoryCoordinator:
    def __init__(self) -> None:
        self._entries: Dict[str, MemoryEntry] = {}
        self._by_owner: Dict[str, List[str]] = {}
        self._by_key: Dict[str, List[str]] = {}
    def put(self, entry: MemoryEntry) -> MemoryEntry:
        self._entries[entry.entry_id] = entry
        self._by_owner.setdefault(entry.owner_id, []).append(entry.entry_id)
        self._by_key.setdefault(entry.key, []).append(entry.entry_id)
        return entry
    def get(self, entry_id: str) -> Optional[MemoryEntry]:
        return self._entries.get(entry_id)
    def query(self, *, owner_id=None, key=None, scope=None, tags=None) -> List[MemoryEntry]:
        candidates = list(self._entries.values())
        if owner_id: candidates = [e for e in candidates if e.owner_id == owner_id]
        if key: candidates = [e for e in candidates if e.key == key]
        if scope: candidates = [e for e in candidates if e.scope == scope]
        if tags:
            tag_set = set(tags)
            candidates = [e for e in candidates if tag_set.intersection(e.tags)]
        return candidates
