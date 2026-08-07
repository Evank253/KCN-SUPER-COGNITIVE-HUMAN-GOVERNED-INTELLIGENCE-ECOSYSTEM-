"""
Knowledge Core — Session / Working Memory
Short-term context for agents and human sessions.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import time
import uuid


class SessionMemory:
    """
    Per-session working memory with TTL and optional promotion to long-term store.
    """

    def __init__(self, default_ttl_seconds: int = 3600):
        self.default_ttl = default_ttl_seconds
        self._sessions: Dict[str, Dict[str, Any]] = {}

    def create_session(
        self,
        *,
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ttl_seconds: Optional[int] = None,
    ) -> str:
        sid = str(uuid.uuid4())
        now = time.time()
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        self._sessions[sid] = {
            "session_id": sid,
            "user_id": user_id,
            "agent_id": agent_id,
            "metadata": metadata or {},
            "created_at": now,
            "expires_at": now + ttl,
            "turns": [],
            "context": {},
        }
        return sid

    def _alive(self, session_id: str) -> bool:
        s = self._sessions.get(session_id)
        if not s:
            return False
        if time.time() > s["expires_at"]:
            del self._sessions[session_id]
            return False
        return True

    def append_turn(
        self,
        session_id: str,
        role: str,
        content: str,
        *,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        if not self._alive(session_id):
            return False
        self._sessions[session_id]["turns"].append(
            {
                "role": role,
                "content": content,
                "tool_calls": tool_calls or [],
                "metadata": metadata or {},
                "ts": time.time(),
            }
        )
        return True

    def set_context(self, session_id: str, key: str, value: Any) -> bool:
        if not self._alive(session_id):
            return False
        self._sessions[session_id]["context"][key] = value
        return True

    def get_context(self, session_id: str, key: Optional[str] = None) -> Any:
        if not self._alive(session_id):
            return None
        ctx = self._sessions[session_id]["context"]
        if key is None:
            return ctx
        return ctx.get(key)

    def get_turns(self, session_id: str, last_n: Optional[int] = None) -> List[Dict[str, Any]]:
        if not self._alive(session_id):
            return []
        turns = self._sessions[session_id]["turns"]
        if last_n is not None:
            return turns[-last_n:]
        return turns

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        if not self._alive(session_id):
            return None
        return self._sessions[session_id]

    def close(self, session_id: str) -> bool:
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    def active_count(self) -> int:
        # purge expired
        for sid in list(self._sessions.keys()):
            self._alive(sid)
        return len(self._sessions)
