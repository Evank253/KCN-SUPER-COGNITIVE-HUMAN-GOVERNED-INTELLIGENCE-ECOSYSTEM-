
"""
Security utilities — JWT token creation and validation.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings


settings = get_settings()

# Password hashing
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# JWT configuration
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    """
    Hash a user password before storing it.
    """
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    """
    Verify a password against its stored hash.
    """
    return pwd_context.verify(
        plain_password,
        hashed_password
    )


def create_access_token(
    subject: str | Any,
    expires_delta: timedelta | None = None
) -> str:
    """
    Create JWT access token.
    """

    expire = (
        datetime.now(timezone.utc) + expires_delta
        if expires_delta
        else datetime.now(timezone.utc) + timedelta(minutes=30)
    )

    payload = {
        "sub": str(subject),
        "exp": expire,
        "type": "access"
    }

    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=ALGORITHM
    )


def create_refresh_token(
    subject: str | Any
) -> str:
    """
    Create long-lived refresh token.
    """

    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.jwt_refresh_token_expire_days
    )

    payload = {
        "sub": str(subject),
        "exp": expire,
        "type": "refresh"
    }

    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=ALGORITHM
    )


def decode_token(token: str) -> dict:
    """
    Validate and decode JWT token.
    """

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[ALGORITHM]
        )

        return payload

    except JWTError as exc:
        raise ValueError(
            "Invalid authentication token"
        ) from exc