"""Knowledge node synchronization."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Optional, Set
from pydantic import BaseModel, Field
import uuid


class KnowledgeNode(BaseModel):
    node_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    label: str
    node_type: str
    properties: Dict[str, str] = Field(default_factory=dict)
    source_subsystem: str
    confidence: float = 1.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    related_ids: List[str] = Field(default_factory=list)


class KnowledgeSync:
    def __init__(self) -> None:
        self._nodes: Dict[str, KnowledgeNode] = {}
        self._label_index: Dict[str, Set[str]] = {}

    def upsert(self, node: KnowledgeNode) -> KnowledgeNode:
        node.updated_at = datetime.now(timezone.utc)
        self._nodes[node.node_id] = node
        self._label_index.setdefault(node.label, set()).add(node.node_id)
        return node

    def get(self, node_id: str) -> Optional[KnowledgeNode]:
        return self._nodes.get(node_id)

    def find_by_label(self, label: str) -> List[KnowledgeNode]:
        ids = self._label_index.get(label, set())
        return [self._nodes[i] for i in ids if i in self._nodes]

    def list_by_source(self, source_subsystem: str) -> List[KnowledgeNode]:
        return [n for n in self._nodes.values() if n.source_subsystem == source_subsystem]
