"""
Agent Pydantic schemas — request bodies and response models.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class AgentCreate(BaseModel):
    """Request body for creating a new agent."""

    name: str = Field(..., min_length=1, max_length=128)
    agent_type: str = Field(default="general", max_length=64)
    description: str | None = Field(None, max_length=1024)
    permissions: list[str] = Field(default_factory=list)
    configuration: dict = Field(default_factory=dict)


class AgentUpdate(BaseModel):
    """Partial update for an existing agent."""

    name: str | None = Field(None, min_length=1, max_length=128)
    agent_type: str | None = Field(None, max_length=64)
    description: str | None = Field(None, max_length=1024)
    permissions: list[str] | None = None
    configuration: dict | None = None
    status: Literal["inactive", "active", "paused"] | None = None


class AgentRead(BaseModel):
    """Agent response schema."""

    model_config = {"from_attributes": True}

    id: str
    name: str
    agent_type: str
    owner_id: str
    description: str | None
    permissions: list
    configuration: dict
    status: Literal["inactive", "active", "paused"]
    created_at: datetime
    updated_at: datetime
