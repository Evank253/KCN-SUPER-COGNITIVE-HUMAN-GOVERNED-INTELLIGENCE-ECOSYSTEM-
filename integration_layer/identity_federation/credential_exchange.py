"""Credential issuance and exchange between subsystems."""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
import uuid
import hashlib
import secrets


class Credential(BaseModel):
    credential_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    identity_id: str
    scope: List[str] = Field(default_factory=list)
    issued_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime
    token_hash: str
    metadata: Dict[str, str] = Field(default_factory=dict)
    revoked: bool = False


class CredentialExchange:
    def __init__(self, default_ttl: timedelta = timedelta(hours=1)) -> None:
        self._credentials: Dict[str, Credential] = {}
        self._default_ttl = default_ttl

    def issue(self, identity_id: str, scope: List[str], ttl: Optional[timedelta] = None,
              metadata: Optional[Dict[str, str]] = None) -> tuple:
        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        expires = datetime.now(timezone.utc) + (ttl or self._default_ttl)
        cred = Credential(identity_id=identity_id, scope=scope, expires_at=expires,
                          token_hash=token_hash, metadata=metadata or {})
        self._credentials[cred.credential_id] = cred
        return raw_token, cred

    def validate(self, raw_token: str) -> Optional[Credential]:
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        for cred in self._credentials.values():
            if cred.token_hash == token_hash and not cred.revoked:
                if datetime.now(timezone.utc) < cred.expires_at:
                    return cred
        return None

    def revoke(self, credential_id: str) -> None:
        if credential_id in self._credentials:
            self._credentials[credential_id].revoked = True
