"""
Memory API routes — Federated Memory Service exposure.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# Import path assumes knowledge is on PYTHONPATH or mounted; for backend isolation
# we use a thin relative import via sys.path adjustment if needed.
import sys
from pathlib import Path

_repo_root = Path(__file__).resolve().parents[3]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from knowledge.memory.federated_memory import memory_service  # noqa: E402

router = APIRouter(prefix="/memory", tags=["Memory"])


class RememberRequest(BaseModel):
    embedding: List[float]
    payload: Dict[str, Any]
    verified: bool = False
    human_approved: bool = False
    source: str = "api"
    tags: Optional[List[str]] = None
    vector_id: Optional[str] = None


class RecallRequest(BaseModel):
    query_embedding: List[float]
    top_k: int = Field(default=5, ge=1, le=50)
    require_verified: bool = True
    require_human_approved: bool = False
    tags: Optional[List[str]] = None
    min_similarity: float = 0.0


class OpenSessionRequest(BaseModel):
    user_id: Optional[str] = None
    agent_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    ttl_seconds: Optional[int] = None


class AddTurnRequest(BaseModel):
    session_id: str
    role: str
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None


@router.get("/health")
def memory_health():
    return memory_service.health()


@router.post("/remember")
def remember(body: RememberRequest):
    return memory_service.remember(
        body.embedding,
        body.payload,
        verified=body.verified,
        human_approved=body.human_approved,
        source=body.source,
        tags=body.tags,
        vector_id=body.vector_id,
    )


@router.post("/recall")
def recall(body: RecallRequest):
    return {
        "results": memory_service.recall(
            body.query_embedding,
            top_k=body.top_k,
            require_verified=body.require_verified,
            require_human_approved=body.require_human_approved,
            tags=body.tags,
            min_similarity=body.min_similarity,
        )
    }


@router.post("/sessions")
def open_session(body: OpenSessionRequest):
    sid = memory_service.open_session(
        user_id=body.user_id,
        agent_id=body.agent_id,
        metadata=body.metadata,
        ttl_seconds=body.ttl_seconds,
    )
    return {"session_id": sid}


@router.post("/sessions/turn")
def add_turn(body: AddTurnRequest):
    ok = memory_service.add_turn(
        body.session_id,
        body.role,
        body.content,
        tool_calls=body.tool_calls,
        metadata=body.metadata,
    )
    if not ok:
        raise HTTPException(status_code=404, detail="Session not found or expired")
    return {"status": "ok"}


@router.get("/sessions/{session_id}")
def get_session(session_id: str):
    ctx = memory_service.session_context(session_id)
    if ctx is None:
        raise HTTPException(status_code=404, detail="Session not found or expired")
    return ctx


@router.get("/federation")
def list_federation():
    return {"adapters": memory_service.list_federation_adapters()}
