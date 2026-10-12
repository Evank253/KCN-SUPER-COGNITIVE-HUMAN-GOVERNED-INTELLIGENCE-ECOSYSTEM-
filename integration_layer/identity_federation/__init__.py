"""Identity Federation – unified identity, credentials, and permission bridging."""

from .unified_identity import UnifiedIdentity, IdentityRecord, IdentityType
from .credential_exchange import CredentialExchange, Credential
from .permission_bridge import PermissionBridge, Permission, AccessDecision

__all__ = [
    "UnifiedIdentity",
    "IdentityRecord",
    "IdentityType",
    "CredentialExchange",
    "Credential",
    "PermissionBridge",
    "Permission",
    "AccessDecision",
]
