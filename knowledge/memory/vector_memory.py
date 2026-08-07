"""
Knowledge Core — Vector Memory
Embedding store for semantic similarity search.
Mirrors Global-Intelligence data_fabric/knowledge_storage/vector_memory.py patterns.
Designed for later Qdrant / Chroma / FAISS backends while remaining dependency-light.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import math
import time
import uuid


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


class VectorMemory:
    """
    In-memory vector store with provenance and governance metadata.
    Only verified / human-approved payloads should be indexed (enforced upstream).
    """

    def __init__(self, namespace: str = "kcn_default"):
        self.namespace = namespace
        self._vectors: List[Dict[str, Any]] = []

    def index(
        self,
        embedding: List[float],
        payload: Dict[str, Any],
        *,
        vector_id: Optional[str] = None,
        source: str = "local",
        verified: bool = False,
        human_approved: bool = False,
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        vid = vector_id or str(uuid.uuid4())
        record = {
            "id": vid,
            "namespace": self.namespace,
            "embedding": embedding,
            "payload": payload,
            "source": source,
            "verified": verified,
            "human_approved": human_approved,
            "tags": tags or [],
            "indexed_at": time.time(),
        }
        self._vectors.append(record)
        return {
            "vector_id": vid,
            "index_status": "INDEXED",
            "namespace": self.namespace,
            "verified": verified,
            "human_approved": human_approved,
        }

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        *,
        min_similarity: float = 0.0,
        require_verified: bool = False,
        require_human_approved: bool = False,
        tags: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for v in self._vectors:
            if require_verified and not v.get("verified"):
                continue
            if require_human_approved and not v.get("human_approved"):
                continue
            if tags:
                if not set(tags).intersection(set(v.get("tags") or [])):
                    continue
            score = _cosine_similarity(query_embedding, v["embedding"])
            if score >= min_similarity:
                results.append(
                    {
                        "id": v["id"],
                        "payload": v["payload"],
                        "similarity_score": round(score, 6),
                        "source": v.get("source"),
                        "verified": v.get("verified"),
                        "human_approved": v.get("human_approved"),
                        "tags": v.get("tags"),
                        "indexed_at": v.get("indexed_at"),
                    }
                )
        results.sort(key=lambda r: r["similarity_score"], reverse=True)
        return results[:top_k]

    def get(self, vector_id: str) -> Optional[Dict[str, Any]]:
        for v in self._vectors:
            if v["id"] == vector_id:
                return {k: v[k] for k in v if k != "embedding"}
        return None

    def delete(self, vector_id: str) -> bool:
        before = len(self._vectors)
        self._vectors = [v for v in self._vectors if v["id"] != vector_id]
        return len(self._vectors) < before

    def stats(self) -> Dict[str, Any]:
        verified = sum(1 for v in self._vectors if v.get("verified"))
        approved = sum(1 for v in self._vectors if v.get("human_approved"))
        return {
            "namespace": self.namespace,
            "total_vectors": len(self._vectors),
            "verified_count": verified,
            "human_approved_count": approved,
        }
