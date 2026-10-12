"""Mission pipeline – high-level goal tracking."""
from __future__ import annotations
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import uuid

class MissionStatus(str, Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Mission(BaseModel):
    mission_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str = ""
    owner_id: str
    status: MissionStatus = MissionStatus.DRAFT
    priority: int = 5
    objectives: List[str] = Field(default_factory=list)
    assigned_subsystems: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

class MissionPipeline:
    def __init__(self) -> None:
        self._missions: Dict[str, Mission] = {}
    def create(self, mission: Mission) -> Mission:
        self._missions[mission.mission_id] = mission
        return mission
    def get(self, mission_id: str) -> Optional[Mission]:
        return self._missions.get(mission_id)
    def update_status(self, mission_id: str, status: MissionStatus) -> Mission:
        mission = self._missions[mission_id]
        mission.status = status
        mission.updated_at = datetime.now(timezone.utc)
        if status == MissionStatus.COMPLETED:
            mission.completed_at = mission.updated_at
        return mission
    def list_by_status(self, status: MissionStatus) -> List[Mission]:
        return [m for m in self._missions.values() if m.status == status]
