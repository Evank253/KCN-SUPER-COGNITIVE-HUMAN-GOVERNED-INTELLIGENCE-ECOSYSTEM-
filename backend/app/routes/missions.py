"""
Mission routes — create and retrieve missions.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.agent import Agent
from app.models.audit_log import AuditLog
from app.models.mission import Mission
from app.models.user import User
from app.schemas.mission import MissionCreate, MissionRead
from app.security.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/missions")


@router.post(
    "/create",
    response_model=MissionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create mission",
)
async def create_mission(
    body: MissionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MissionRead:
    """
    Create a new mission.

    If agent_id is provided, the agent must be owned by the current user.
    """
    if body.agent_id:
        result = await db.execute(
            select(Agent).where(
                Agent.id == body.agent_id, Agent.owner_id == current_user.id
            )
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found",
            )

    mission = Mission(
        title=body.title,
        description=body.description,
        agent_id=body.agent_id,
        requester_id=current_user.id,
        status="pending",
    )
    db.add(mission)
    await db.flush()

    db.add(
        AuditLog(
            action="mission.create",
            resource_type="Mission",
            resource_id=mission.id,
            user_id=current_user.id,
            outcome="success",
        )
    )
    await db.commit()
    await db.refresh(mission)

    logger.info("Mission created: id=%s requester=%s", mission.id, current_user.id)
    return MissionRead.model_validate(mission)


@router.get(
    "",
    response_model=list[MissionRead],
    status_code=status.HTTP_200_OK,
    summary="List missions",
)
async def list_missions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[MissionRead]:
    """Return all missions created by the current user."""
    result = await db.execute(
        select(Mission).where(Mission.requester_id == current_user.id)
    )
    missions = result.scalars().all()
    return [MissionRead.model_validate(m) for m in missions]


@router.get(
    "/{mission_id}",
    response_model=MissionRead,
    status_code=status.HTTP_200_OK,
    summary="Get mission",
)
async def get_mission(
    mission_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MissionRead:
    """Return a specific mission created by the current user."""
    result = await db.execute(
        select(Mission).where(
            Mission.id == mission_id, Mission.requester_id == current_user.id
        )
    )
    mission = result.scalar_one_or_none()
    if not mission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mission not found",
        )
    return MissionRead.model_validate(mission)
