"""
Audit log Pydantic schemas — response models only (logs are immutable).
"""

from datetime import datetime

from pydantic import BaseModel


class AuditLogRead(BaseModel):
    """Audit log entry response schema."""

    model_config = {"from_attributes": True}

    id: str
    action: str
    resource_type: str | None
    resource_id: str | None
    user_id: str | None
    agent_id: str | None
    permission_approved: bool
    outcome: str | None
    timestamp: datetime
