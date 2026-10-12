"""Swarm management – coordinated multi-agent groups."""
from __future__ import annotations
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
import uuid

class SwarmStatus(str, Enum):
    FORMING = "forming"
    ACTIVE = "active"
    PAUSED = "paused"
    DISSOLVED = "dissolved"

class SwarmMember(BaseModel):
    agent_id: str
    role: str
    joined_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Swarm(BaseModel):
    swarm_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    goal: str
    status: SwarmStatus = SwarmStatus.FORMING
    members: List[SwarmMember] = Field(default_factory=list)
    mission_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, str] = Field(default_factory=dict)

class SwarmManager:
    def __init__(self) -> None:
        self._swarms: Dict[str, Swarm] = {}
    def create(self, swarm: Swarm) -> Swarm:
        self._swarms[swarm.swarm_id] = swarm
        return swarm
    def get(self, swarm_id: str) -> Optional[Swarm]:
        return self._swarms.get(swarm_id)
    def add_member(self, swarm_id: str, member: SwarmMember) -> Swarm:
        swarm = self._swarms[swarm_id]
        if any(m.agent_id == member.agent_id for m in swarm.members):
            raise ValueError(f"Agent {member.agent_id} already in swarm")
        swarm.members.append(member)
        return swarm
    def remove_member(self, swarm_id: str, agent_id: str) -> Swarm:
        swarm = self._swarms[swarm_id]
        swarm.members = [m for m in swarm.members if m.agent_id != agent_id]
        return swarm
    def set_status(self, swarm_id: str, status: SwarmStatus) -> Swarm:
        swarm = self._swarms[swarm_id]
        swarm.status = status
        return swarm
    def list_active(self) -> List[Swarm]:
        return [s for s in self._swarms.values() if s.status == SwarmStatus.ACTIVE]
