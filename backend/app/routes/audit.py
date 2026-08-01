"""
Audit log routes — read-only access to the audit trail.
"""

import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.audit import AuditLogRead
from app.security.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/audit-logs")


@router.get(
    "",
    response_model=list[AuditLogRead],
    status_code=status.HTTP_200_OK,
    summary="Get audit trail",
)
async def list_audit_logs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[AuditLogRead]:
    """
    Return audit log entries.

    - Regular users see only their own entries.
    - ADMIN users see all entries.
    Results are ordered by most recent first (limit 200).
    """
    query = select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(200)
    if current_user.role != "ADMIN":
        query = query.where(AuditLog.user_id == current_user.id)

    result = await db.execute(query)
    logs = result.scalars().all()
    return [AuditLogRead.model_validate(log) for log in logs]
