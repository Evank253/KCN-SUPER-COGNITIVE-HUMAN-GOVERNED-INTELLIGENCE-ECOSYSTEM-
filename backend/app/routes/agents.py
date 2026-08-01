"""
Agent routes — CRUD for user-owned agents.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.agent import Agent
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.agent import AgentCreate, AgentRead, AgentUpdate
from app.security.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/agents")


@router.post(
    "/create",
    response_model=AgentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create agent",
)
async def create_agent(
    body: AgentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AgentRead:
    """Create a new agent owned by the current user."""
    agent = Agent(
        owner_id=current_user.id,
        name=body.name,
        agent_type=body.agent_type,
        description=body.description,
        permissions=body.permissions,
        configuration=body.configuration,
        status="inactive",
    )
    db.add(agent)
    await db.flush()

    db.add(
        AuditLog(
            action="agent.create",
            resource_type="Agent",
            resource_id=agent.id,
            user_id=current_user.id,
            outcome="success",
        )
    )
    await db.commit()
    await db.refresh(agent)

    logger.info("Agent created: id=%s owner=%s", agent.id, current_user.id)
    return AgentRead.model_validate(agent)


@router.get(
    "",
    response_model=list[AgentRead],
    status_code=status.HTTP_200_OK,
    summary="List agents",
)
async def list_agents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[AgentRead]:
    """Return all agents owned by the current user."""
    result = await db.execute(
        select(Agent).where(Agent.owner_id == current_user.id)
    )
    agents = result.scalars().all()
    return [AgentRead.model_validate(a) for a in agents]


@router.get(
    "/{agent_id}",
    response_model=AgentRead,
    status_code=status.HTTP_200_OK,
    summary="Get agent",
)
async def get_agent(
    agent_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AgentRead:
    """Return a specific agent owned by the current user."""
    agent = await _get_owned_agent(agent_id, current_user.id, db)
    return AgentRead.model_validate(agent)


@router.put(
    "/{agent_id}",
    response_model=AgentRead,
    status_code=status.HTTP_200_OK,
    summary="Update agent",
)
async def update_agent(
    agent_id: str,
    body: AgentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AgentRead:
    """Update a specific agent owned by the current user."""
    agent = await _get_owned_agent(agent_id, current_user.id, db)

    update_data = body.model_dump(exclude_none=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No fields provided to update",
        )

    for field, value in update_data.items():
        setattr(agent, field, value)

    db.add(
        AuditLog(
            action="agent.update",
            resource_type="Agent",
            resource_id=agent.id,
            user_id=current_user.id,
            outcome="success",
        )
    )
    await db.commit()
    await db.refresh(agent)

    logger.info("Agent updated: id=%s", agent.id)
    return AgentRead.model_validate(agent)


@router.delete(
    "/{agent_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete agent",
)
async def delete_agent(
    agent_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a specific agent owned by the current user."""
    agent = await _get_owned_agent(agent_id, current_user.id, db)

    db.add(
        AuditLog(
            action="agent.delete",
            resource_type="Agent",
            resource_id=agent.id,
            user_id=current_user.id,
            outcome="success",
        )
    )
    await db.delete(agent)
    await db.commit()

    logger.info("Agent deleted: id=%s", agent.id)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


async def _get_owned_agent(
    agent_id: str, owner_id: str, db: AsyncSession
) -> Agent:
    """Fetch an agent by ID, verifying ownership. Raises 404 if not found."""
    result = await db.execute(
        select(Agent).where(Agent.id == agent_id, Agent.owner_id == owner_id)
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )
    return agent
