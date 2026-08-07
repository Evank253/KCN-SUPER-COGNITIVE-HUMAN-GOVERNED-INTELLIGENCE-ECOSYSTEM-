"""
Knowledge Core — Federated Memory Service
Unifies local vector + session memory and provides hooks for cross-repo federation
(Global-Intelligence, vibe-developer, KCN_SINGULARITY_MASTER, etc.).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .vector_memory import VectorMemory
from .session_memory import SessionMemory


class FederatedMemoryService:
    """
    Single entry point for memory operations across the KCN ecosystem.
    Local store is authoritative; remote federation is pluggable.
    """

    def __init__(self, namespace: str = "kcn_super_cognitive"):
        self.namespace = namespace
        self.vector = VectorMemory(namespace=namespace)
        self.session = SessionMemory()
        # Registered remote adapters (name -> callable or config)
        self._federation_adapters: Dict[str, Dict[str, Any]] = {}

    # ── Vector (long-term) ──────────────────────────────────────────────

    def remember(
        self,
        embedding: List[float],
        payload: Dict[str, Any],
        *,
        verified: bool = False,
        human_approved: bool = False,
        source: str = "local",
        tags: Optional[List[str]] = None,
        vector_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        return self.vector.index(
            embedding,
            payload,
            vector_id=vector_id,
            source=source,
            verified=verified,
            human_approved=human_approved,
            tags=tags,
        )

    def recall(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        *,
        require_verified: bool = True,
        require_human_approved: bool = False,
        tags: Optional[List[str]] = None,
        min_similarity: float = 0.0,
    ) -> List[Dict[str, Any]]:
        return self.vector.search(
            query_embedding,
            top_k=top_k,
            min_similarity=min_similarity,
            require_verified=require_verified,
            require_human_approved=require_human_approved,
            tags=tags,
        )

    # ── Session (working) ───────────────────────────────────────────────

    def open_session(
        self,
        *,
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ttl_seconds: Optional[int] = None,
    ) -> str:
        return self.session.create_session(
            user_id=user_id,
            agent_id=agent_id,
            metadata=metadata,
            ttl_seconds=ttl_seconds,
        )

    def add_turn(
        self,
        session_id: str,
        role: str,
        content: str,
        *,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        return self.session.append_turn(
            session_id, role, content, tool_calls=tool_calls, metadata=metadata
        )

    def session_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self.session.get_session(session_id)

    # ── Federation ──────────────────────────────────────────────────────

    def register_federation_adapter(
        self,
        name: str,
        *,
        endpoint: Optional[str] = None,
        repo: Optional[str] = None,
        description: str = "",
        capabilities: Optional[List[str]] = None,
    ) -> None:
        self._federation_adapters[name] = {
            "endpoint": endpoint,
            "repo": repo,
            "description": description,
            "capabilities": capabilities or ["vector_search", "session_sync"],
            "status": "registered",
        }

    def list_federation_adapters(self) -> Dict[str, Dict[str, Any]]:
        return dict(self._federation_adapters)

    def health(self) -> Dict[str, Any]:
        return {
            "namespace": self.namespace,
            "vector": self.vector.stats(),
            "active_sessions": self.session.active_count(),
            "federation_adapters": list(self._federation_adapters.keys()),
        }


# Singleton for simple import usage across backend routes
memory_service = FederatedMemoryService()

# Pre-register known ecosystem peers (hooks only; actual remote calls are future work)
memory_service.register_federation_adapter(
    "global_intelligence",
    repo="Evank253/Global-Intelligence",
    description="Primary agent runtime + data fabric vector memory",
    capabilities=["vector_search", "tool_registry", "agent_runtime"],
)
memory_service.register_federation_adapter(
    "vibe_developer",
    repo="Evank253/vibe-developer",
    description="Developer UI + terminal / AI service layer",
    capabilities=["session_context", "chat_history"],
)
memory_service.register_federation_adapter(
    "singularity_master",
    repo="Evank253/KCN_SINGULARITY_MASTER",
    description="Apex coordination scaffold",
    capabilities=["orchestration_hooks"],
)
