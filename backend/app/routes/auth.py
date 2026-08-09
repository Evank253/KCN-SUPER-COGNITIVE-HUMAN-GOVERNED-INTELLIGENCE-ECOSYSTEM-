"""
Authentication routes — login, token refresh, logout.
"""

import logging
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_oauth_state_token,
    create_refresh_token,
    decode_token,
    is_authorized_github_admin,
    verify_oauth_state_token,
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


# ---------------------------------------------------------------------------
# GitHub OAuth — admin sign-in
# ---------------------------------------------------------------------------
#
# Admin identity is verified by signing in with GitHub rather than a shared
# password. Only usernames listed in `settings.github_admin_usernames` are
# ever issued an admin JWT — everyone else who completes GitHub OAuth still
# gets rejected with 403. Requires a GitHub OAuth App to be registered
# (see DEPLOYMENT.md for setup steps) and the
# GITHUB_CLIENT_ID / GITHUB_CLIENT_SECRET env vars set on the backend host.

GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USER_API_URL = "https://api.github.com/user"


@router.get(
    "/github/login",
    summary="Start GitHub OAuth sign-in (admin)",
)
async def github_login() -> RedirectResponse:
    """
    Redirect the browser to GitHub's OAuth authorization page.

    A signed, short-lived `state` token is included to prevent CSRF —
    the callback route rejects any request whose state doesn't verify.
    """
    if not settings.github_client_id:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GitHub OAuth is not configured on this server.",
        )

    state = create_oauth_state_token()
    params = {
        "client_id": settings.github_client_id,
        "redirect_uri": settings.github_oauth_redirect_uri,
        "scope": "read:user",
        "state": state,
        "allow_signup": "false",
    }
    return RedirectResponse(url=f"{GITHUB_AUTHORIZE_URL}?{urlencode(params)}")


@router.get(
    "/github/callback",
    summary="GitHub OAuth callback (admin)",
)
async def github_callback(code: str, state: str) -> RedirectResponse:
    """
    Handle GitHub's redirect back after the user approves/denies access.

    Exchanges the temporary `code` for an access token, fetches the GitHub
    identity, and — only if that username is on the admin allowlist — issues
    our own JWT pair and redirects back to the frontend with them attached.
    Any failure redirects to the frontend login page with an error flag
    instead of raising a raw API error, since this endpoint is hit by the
    browser directly (not called from application code).
    """
    login_failed_redirect = f"{settings.frontend_url}/login?error=github_auth_failed"

    if not verify_oauth_state_token(state):
        logger.warning("GitHub OAuth callback rejected: invalid/expired state")
        return RedirectResponse(url=login_failed_redirect)

    if not settings.github_client_id or not settings.github_client_secret:
        logger.error("GitHub OAuth callback hit but client credentials not configured")
        return RedirectResponse(url=login_failed_redirect)

    async with httpx.AsyncClient(timeout=10.0) as client:
        token_resp = await client.post(
            GITHUB_TOKEN_URL,
            headers={"Accept": "application/json"},
            data={
                "client_id": settings.github_client_id,
                "client_secret": settings.github_client_secret,
                "code": code,
                "redirect_uri": settings.github_oauth_redirect_uri,
            },
        )

        if token_resp.status_code != 200:
            logger.warning(
                "GitHub token exchange failed: status=%s", token_resp.status_code
            )
            return RedirectResponse(url=login_failed_redirect)

        token_data = token_resp.json()
        github_access_token = token_data.get("access_token")
        if not github_access_token:
            logger.warning("GitHub token exchange returned no access_token")
            return RedirectResponse(url=login_failed_redirect)

        user_resp = await client.get(
            GITHUB_USER_API_URL,
            headers={
                "Authorization": f"Bearer {github_access_token}",
                "Accept": "application/vnd.github+json",
            },
        )

        if user_resp.status_code != 200:
            logger.warning(
                "GitHub user lookup failed: status=%s", user_resp.status_code
            )
            return RedirectResponse(url=login_failed_redirect)

        github_user = user_resp.json()
        github_username = github_user.get("login", "")

    if not github_username or not is_authorized_github_admin(github_username):
        logger.warning(
            "GitHub OAuth login rejected: username=%s is not an authorized admin",
            github_username,
        )
        return RedirectResponse(
            url=f"{settings.frontend_url}/login?error=not_authorized"
        )

    access_token = create_access_token(
        subject=github_username,
        additional_claims={"roles": ["admin"], "auth_provider": "github"},
    )
    refresh_token = create_refresh_token(subject=github_username)

    logger.info("Admin authenticated via GitHub: username=%s", github_username)

    redirect_params = urlencode(
        {"access_token": access_token, "refresh_token": refresh_token}
    )
    return RedirectResponse(url=f"{settings.frontend_url}/auth/callback?{redirect_params}")
