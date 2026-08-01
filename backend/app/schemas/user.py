"""
User Pydantic schemas — request bodies and response models.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field

# ---------------------------------------------------------------------------
# Sub-schemas
# ---------------------------------------------------------------------------


class ProfileRead(BaseModel):
    """Embedded profile snapshot returned with user responses."""

    model_config = {"from_attributes": True}

    display_name: str | None = None
    bio: str | None = None
    capabilities: list = Field(default_factory=list)
    goals: list = Field(default_factory=list)
    learning_paths: list = Field(default_factory=list)


class ProfileUpdate(BaseModel):
    """Fields the user may update on their profile."""

    display_name: str | None = Field(None, max_length=128)
    bio: str | None = Field(None, max_length=2048)
    capabilities: list | None = None
    goals: list | None = None
    learning_paths: list | None = None


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------


class UserCreate(BaseModel):
    """Registration request body."""

    username: str = Field(..., min_length=3, max_length=128)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=256)


class UserUpdate(BaseModel):
    """Partial user update (profile fields)."""

    profile: ProfileUpdate | None = None


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------


class UserRead(BaseModel):
    """User response — never exposes hashed_password."""

    model_config = {"from_attributes": True}

    id: str
    username: str
    email: str
    role: Literal["ADMIN", "BUILDER", "USER", "AGENT"]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    profile: ProfileRead | None = None
