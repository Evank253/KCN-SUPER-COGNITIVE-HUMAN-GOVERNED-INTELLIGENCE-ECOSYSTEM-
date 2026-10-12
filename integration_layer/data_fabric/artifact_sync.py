"""Artifact synchronization across subsystems."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
import uuid
import hashlib


class Artifact(BaseModel):
    artifact_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    content_type: str
    content_hash: str
    size_bytes: int
    source_subsystem: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, str] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)


class ArtifactSync:
    def __init__(self) -> None:
        self._artifacts: Dict[str, Artifact] = {}

    @staticmethod
    def compute_hash(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def register(self, name: str, content_type: str, data: bytes, source_subsystem: str,
                 metadata: Optional[Dict[str, str]] = None, tags: Optional[List[str]] = None) -> Artifact:
        artifact = Artifact(
            name=name, content_type=content_type,
            content_hash=self.compute_hash(data), size_bytes=len(data),
            source_subsystem=source_subsystem, metadata=metadata or {}, tags=tags or [],
        )
        self._artifacts[artifact.artifact_id] = artifact
        return artifact

    def get(self, artifact_id: str) -> Optional[Artifact]:
        return self._artifacts.get(artifact_id)

    def find_by_hash(self, content_hash: str) -> Optional[Artifact]:
        for a in self._artifacts.values():
            if a.content_hash == content_hash:
                return a
        return None

    def list_by_source(self, source_subsystem: str) -> List[Artifact]:
        return [a for a in self._artifacts.values() if a.source_subsystem == source_subsystem]
