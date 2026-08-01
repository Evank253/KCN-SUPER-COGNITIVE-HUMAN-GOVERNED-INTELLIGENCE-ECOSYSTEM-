"""
User ORM model.

Stores account identity, hashed credentials, role, and status.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class UserRole(str):
    ADMIN = "ADMIN"
    BUILDER = "BUILDER"
    USER = "USER"
    AGENT = "AGENT"


class User(Base):
    """Registered KCN user account."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    username: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(256), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(256), nullable=False)
    role: Mapped[str] = mapped_column(
        Enum("ADMIN", "BUILDER", "USER", "AGENT", name="user_role"),
        nullable=False,
        default="USER",
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    profile: Mapped["Profile"] = relationship(  # noqa: F821
        "Profile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    agents: Mapped[list["Agent"]] = relationship(  # noqa: F821
        "Agent", back_populates="owner", cascade="all, delete-orphan"
    )
    audit_logs: Mapped[list["AuditLog"]] = relationship(  # noqa: F821
        "AuditLog", back_populates="actor_user", foreign_keys="AuditLog.user_id"
    )
