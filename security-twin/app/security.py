"""JWT + password helpers for the twin (stricter claims)."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings
from app.token_blacklist import is_revoked

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def _base_claims(subject: str, token_type: str, lifetime: timedelta) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    return {
        "sub": subject,
        "iss": settings.jwt_issuer,
        "iat": now,
        "exp": now + lifetime,
        "type": token_type,
        "twin": True,
        "jti": str(uuid.uuid4()),
    }


def create_access_token(subject: str, claims: dict[str, Any] | None = None) -> str:
    payload = _base_claims(
        subject,
        "access",
        timedelta(minutes=settings.jwt_access_token_expire_minutes),
    )
    if claims:
        payload.update(claims)
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(subject: str) -> str:
    payload = _base_claims(
        subject,
        "refresh",
        timedelta(days=settings.jwt_refresh_token_expire_days),
    )
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(
    token: str,
    *,
    expected_type: str | None = None,
    check_blacklist: bool = True,
) -> dict[str, Any] | None:
    """
    Strict decode: signature, exp, iss, twin flag, optional type, blacklist.
    Returns payload or None.
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            issuer=settings.jwt_issuer,
            options={
                "require_exp": True,
                "require_iat": True,
                "require_sub": True,
                "verify_iss": True,
            },
        )
    except JWTError:
        return None

    if payload.get("twin") is not True:
        return None
    if expected_type and payload.get("type") != expected_type:
        return None
    if check_blacklist and is_revoked(payload.get("jti")):
        return None
    return payload
