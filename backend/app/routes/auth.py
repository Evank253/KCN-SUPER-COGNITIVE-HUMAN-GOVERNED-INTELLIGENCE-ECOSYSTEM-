"""
Authentication routes — login, token refresh, logout.
"""

import logging

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth")


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


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
# Stub user store (replaced by real database in Phase 2)
# ---------------------------------------------------------------------------

# NOTE: This is a development stub only. Never store credentials in source code.
# Replace with a real user database before any production deployment.
_STUB_USERS = {
    "admin": {
        "username": "admin",
        # bcrypt hash of "changeme" — for development only
        "hashed_password": "$2b$12$6a/QWNzQb5gOTdKvHaAhQO15V07w2iu/1Rgw9IMsr704BWTwkFcEy",
        "roles": ["admin"],
    },
}


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate user",
)
async def login(request: LoginRequest) -> TokenResponse:
    """
    Authenticate a user with username and password.

    Returns JWT access and refresh tokens on success.
    Returns 401 if credentials are invalid.
    """
    user = _STUB_USERS.get(request.username)
    if not user or not verify_password(request.password, user["hashed_password"]):
        logger.warning("Failed login attempt for username=%s", request.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        subject=user["username"],
        additional_claims={"roles": user["roles"]},
    )
    refresh_token = create_refresh_token(subject=user["username"])

    logger.info("User authenticated: username=%s", user["username"])
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
async def refresh_token(request: RefreshRequest) -> AccessTokenResponse:
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

    username: str = payload.get("sub", "")
    user = _STUB_USERS.get(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    access_token = create_access_token(
        subject=username,
        additional_claims={"roles": user["roles"]},
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

    In Phase 2, this will invalidate the token in the token blacklist.
    Currently returns a success message.
    """
    # TODO(Phase 2): Add token to blacklist / revoke in database
    return MessageResponse(message="Logged out successfully")
