"""Central registry of all KCN subsystems."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class SubsystemStatus(str, Enum):
    REGISTERED = "registered"
    STARTING = "starting"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    STOPPED = "stopped"


class SubsystemInfo(BaseModel):
    subsystem_id: str
    name: str
    phase: str
    version: str
    endpoints: Dict[str, str] = Field(default_factory=dict)
    capabilities: List[str] = Field(default_factory=list)
    status: SubsystemStatus = SubsystemStatus.REGISTERED
    registered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_heartbeat: Optional[datetime] = None
    metadata: Dict[str, str] = Field(default_factory=dict)


class SubsystemRegistry:
    def __init__(self) -> None:
        self._subsystems: Dict[str, SubsystemInfo] = {}

    def register(self, info: SubsystemInfo) -> SubsystemInfo:
        if info.subsystem_id in self._subsystems:
            raise ValueError(f"Subsystem already registered: {info.subsystem_id}")
        self._subsystems[info.subsystem_id] = info
        return info

    def unregister(self, subsystem_id: str) -> None:
        self._subsystems.pop(subsystem_id, None)

    def get(self, subsystem_id: str) -> Optional[SubsystemInfo]:
        return self._subsystems.get(subsystem_id)

    def list_all(self) -> List[SubsystemInfo]:
        return list(self._subsystems.values())

    def list_by_phase(self, phase: str) -> List[SubsystemInfo]:
        return [s for s in self._subsystems.values() if s.phase == phase]

    def list_by_capability(self, capability: str) -> List[SubsystemInfo]:
        return [s for s in self._subsystems.values() if capability in s.capabilities]

    def update_status(self, subsystem_id: str, status: SubsystemStatus) -> None:
        if subsystem_id not in self._subsystems:
            raise KeyError(f"Unknown subsystem: {subsystem_id}")
        self._subsystems[subsystem_id].status = status
        self._subsystems[subsystem_id].last_heartbeat = datetime.now(timezone.utc)

    def heartbeat(self, subsystem_id: str) -> None:
        if subsystem_id not in self._subsystems:
            raise KeyError(f"Unknown subsystem: {subsystem_id}")
        self._subsystems[subsystem_id].last_heartbeat = datetime.now(timezone.utc)
