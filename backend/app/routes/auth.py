"""
Authentication routes — register, login, token refresh, logout.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.database.session import get_db
from app.models.audit_log import AuditLog
from app.models.profile import Profile
from app.models.user import User
from app.schemas.user import UserRead

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth")


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class RegisterRequest(BaseModel):
    """User registration request body."""

    username: str = Field(..., min_length=3, max_length=128)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=256)


class LoginRequest(BaseModel):
    """Login request body."""

    username: str = Field(..., min_length=1, max_length=128)
    password: str = Field(..., min_length=1, max_length=256)


class TokenResponse(BaseModel):
    """Successful authentication response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Access token lifetime in seconds")


class RefreshRequest(BaseModel):
    """Token refresh request body."""

    refresh_token: str


class AccessTokenResponse(BaseModel):
    """Refreshed access token response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
)
async def register(
    request: RegisterRequest, db: AsyncSession = Depends(get_db)
) -> UserRead:
    """
    Register a new KCN user account.

    Creates a User record, an empty Profile, and an audit log entry.
    Returns the created user. Returns 409 if username or email already exists.
    """
    # Check for duplicate username or email
    existing = await db.execute(
        select(User).where(
            (User.username == request.username) | (User.email == request.email)
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already registered",
        )

    user = User(
        username=request.username,
        email=request.email,
        hashed_password=hash_password(request.password),
        role="USER",
        is_active=True,
    )
    db.add(user)
    await db.flush()  # populate user.id before creating child records

    profile = Profile(user_id=user.id)
    audit = AuditLog(
        action="user.register",
        resource_type="User",
        resource_id=user.id,
        user_id=user.id,
        outcome="success",
    )
    db.add(profile)
    db.add(audit)
    await db.commit()

    # Re-fetch with eagerly loaded profile for serialization
    result = await db.execute(
        select(User).options(selectinload(User.profile)).where(User.id == user.id)
    )
    user = result.scalar_one()

    logger.info("New user registered: username=%s id=%s", user.username, user.id)
    return UserRead.model_validate(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate user",
)
async def login(
    request: LoginRequest, db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """
    Authenticate a user with username and password.

    Returns JWT access and refresh tokens on success.
    Returns 401 if credentials are invalid.
    """
    result = await db.execute(select(User).where(User.username == request.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(request.password, user.hashed_password):
        logger.warning("Failed login attempt for username=%s", request.username)
        # Audit failed attempt
        db.add(
            AuditLog(
                action="user.login.failed",
                resource_type="User",
                user_id=None,
                permission_approved=False,
                outcome=f"invalid credentials for username={request.username}",
            )
        )
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )

    access_token = create_access_token(
        subject=user.id,
        additional_claims={"role": user.role, "username": user.username},
    )
    refresh_token = create_refresh_token(subject=user.id)

    db.add(
        AuditLog(
            action="user.login",
            resource_type="User",
            resource_id=user.id,
            user_id=user.id,
            outcome="success",
        )
    )
    await db.commit()

    logger.info("User authenticated: username=%s id=%s", user.username, user.id)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.jwt_access_token_expire_minutes * 60,
    )


@router.post(
    "/refresh",
    response_model=AccessTokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
)
async def refresh_token(
    request: RefreshRequest, db: AsyncSession = Depends(get_db)
) -> AccessTokenResponse:
    """
    Issue a new access token using a valid refresh token.

    Returns 401 if the refresh token is invalid or expired.
    """
    payload = decode_token(request.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: str = payload.get("sub", "")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    access_token = create_access_token(
        subject=user.id,
        additional_claims={"role": user.role, "username": user.username},
    )
    return AccessTokenResponse(
        access_token=access_token,
        expires_in=settings.jwt_access_token_expire_minutes * 60,
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Log out",
)
async def logout() -> MessageResponse:
    """
    Log out the current user.

    Token blacklisting will be added in a future sprint.
    Currently returns a success message.
    """
    return MessageResponse(message="Logged out successfully")
