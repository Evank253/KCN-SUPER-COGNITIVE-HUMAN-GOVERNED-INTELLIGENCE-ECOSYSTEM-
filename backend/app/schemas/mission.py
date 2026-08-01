"""
Mission Pydantic schemas — request bodies and response models.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class MissionCreate(BaseModel):
    """Request body for creating a new mission."""

    title: str = Field(..., min_length=1, max_length=256)
    description: str = Field(..., min_length=1)
    agent_id: str | None = Field(None, description="Optional agent to assign")


class MissionRead(BaseModel):
    """Mission response schema."""

    model_config = {"from_attributes": True}

    id: str
    title: str
    description: str
    agent_id: str | None
    requester_id: str
    status: Literal["pending", "running", "completed", "failed"]
    results: dict | None
    created_at: datetime
    updated_at: datetime
