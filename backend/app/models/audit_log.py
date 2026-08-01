"""
AuditLog ORM model.

Immutable record of every significant action in the KCN ecosystem.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class AuditLog(Base):
    """Immutable audit trail entry."""

    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    action: Mapped[str] = mapped_column(String(256), nullable=False, index=True)
    resource_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    resource_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    user_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    agent_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    permission_approved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    outcome: Mapped[str | None] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    # Relationships
    actor_user: Mapped["User | None"] = relationship(  # noqa: F821
        "User", back_populates="audit_logs", foreign_keys=[user_id]
    )
