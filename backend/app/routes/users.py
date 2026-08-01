"""
User routes — current user profile.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.session import get_db
from app.models.audit_log import AuditLog
from app.models.profile import Profile
from app.models.user import User
from app.schemas.user import ProfileUpdate, UserRead
from app.security.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users")


@router.get(
    "/me",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
    summary="Get current user",
)
async def get_me(current_user: User = Depends(get_current_user)) -> UserRead:
    """Return the authenticated user's account and profile."""
    return UserRead.model_validate(current_user)


@router.put(
    "/profile",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
    summary="Update user profile",
)
async def update_profile(
    body: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserRead:
    """
    Update the authenticated user's profile fields.

    Only provided (non-None) fields are changed.
    """
    update_data = body.model_dump(exclude_none=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No fields provided to update",
        )

    profile = current_user.profile
    if profile is None:
        profile = Profile(user_id=current_user.id)
        db.add(profile)
        await db.flush()

    for field, value in update_data.items():
        setattr(profile, field, value)

    db.add(
        AuditLog(
            action="user.profile.update",
            resource_type="Profile",
            resource_id=profile.id,
            user_id=current_user.id,
            outcome="success",
        )
    )
    await db.commit()

    # Re-fetch with eager-loaded profile for serialization
    result = await db.execute(
        select(User)
        .options(selectinload(User.profile))
        .where(User.id == current_user.id)
    )
    refreshed = result.scalar_one()

    logger.info("Profile updated for user id=%s", current_user.id)
    return UserRead.model_validate(refreshed)
