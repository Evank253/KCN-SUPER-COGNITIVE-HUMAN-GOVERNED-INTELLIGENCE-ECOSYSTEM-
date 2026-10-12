"""Registry of all AI agents running inside the KCN ecosystem."""
from __future__ import annotations
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
import uuid

class AgentStatus(str, Enum):
    REGISTERED = "registered"
    IDLE = "idle"
    BUSY = "busy"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"

class AgentRecord(BaseModel):
    agent_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    agent_type: str
    capabilities: List[str] = Field(default_factory=list)
    identity_id: str
    runtime_subsystem: str
    status: AgentStatus = AgentStatus.REGISTERED
    metadata: Dict[str, str] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_active: Optional[datetime] = None

class AgentRegistry:
    def __init__(self) -> None:
        self._agents: Dict[str, AgentRecord] = {}
    def register(self, agent: AgentRecord) -> AgentRecord:
        self._agents[agent.agent_id] = agent
        return agent
    def get(self, agent_id: str) -> Optional[AgentRecord]:
        return self._agents.get(agent_id)
    def list_by_capability(self, capability: str) -> List[AgentRecord]:
        return [a for a in self._agents.values() if capability in a.capabilities]
    def list_by_status(self, status: AgentStatus) -> List[AgentRecord]:
        return [a for a in self._agents.values() if a.status == status]
    def update_status(self, agent_id: str, status: AgentStatus) -> None:
        agent = self._agents[agent_id]
        agent.status = status
        agent.last_active = datetime.now(timezone.utc)
