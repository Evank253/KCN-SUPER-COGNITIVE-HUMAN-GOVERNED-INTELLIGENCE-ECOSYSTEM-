"""
Security utilities — JWT token creation and validation.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plain-text password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a stored hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    subject: str, additional_claims: dict[str, Any] | None = None
) -> str:
    """Create a signed JWT access token."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_access_token_expire_minutes
    )
    payload: dict[str, Any] = {
        "sub": subject,
        "exp": expire,
        "type": "access",
    }
    if additional_claims:
        payload.update(additional_claims)
    return jwt.encode(
        payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )


def create_refresh_token(subject: str) -> str:
    """Create a signed JWT refresh token."""
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.jwt_refresh_token_expire_days
    )
    payload: dict[str, Any] = {
        "sub": subject,
        "exp": expire,
        "type": "refresh",
    }
    return jwt.encode(
        payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )


def create_oauth_state_token() -> str:
    """Create a short-lived signed token used as the OAuth 'state' parameter.

    This protects the GitHub OAuth redirect against CSRF: we generate it before
    redirecting to GitHub, and require the callback to return the exact same
    signed value. Because it's signed with our JWT secret, an attacker can't
    forge one, and it expires quickly if unused.
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.oauth_state_expire_minutes
    )
    payload: dict[str, Any] = {"exp": expire, "type": "oauth_state"}
    return jwt.encode(
        payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )


def verify_oauth_state_token(token: str) -> bool:
    """Verify a previously issued OAuth state token is valid and unexpired."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload.get("type") == "oauth_state"
    except JWTError as exc:
        logger.warning("OAuth state token verification failed: %s", exc)
        return False


def is_authorized_github_admin(github_username: str) -> bool:
    """Check whether a GitHub username is on the configured admin allowlist."""
    allowed = {
        u.strip().lower()
        for u in settings.github_admin_usernames.split(",")
        if u.strip()
    }
    return github_username.strip().lower() in allowed


def decode_token(token: str) -> dict[str, Any] | None:
    """Decode and validate a JWT token. Returns the payload or None if invalid."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except JWTError as exc:
        logger.warning("JWT decode error: %s", exc)
        return None
