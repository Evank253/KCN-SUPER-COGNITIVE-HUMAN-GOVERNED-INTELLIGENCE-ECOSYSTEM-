# Security Core

The Security Core protects all layers of the KCN ecosystem through identity management, authentication, authorization, encryption, monitoring, threat detection, and audit logging.

## Purpose

Provide shared security services to every subsystem. Security is built in — not added on.

## Modules

| Module | Status |
|---|---|
| Identity Management | Phase 1 (stub) |
| Authentication | Phase 1 (JWT stub) |
| Authorization (RBAC) | Phase 2 |
| Encryption | Phase 3 |
| Monitoring | Phase 2 |
| Threat Detection | Phase 2 |
| Audit System | Phase 2 |

## Dependencies

- None (Security Core has no runtime dependencies on other subsystems)

## Interfaces

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`

## Expansion Points

- MFA support (TOTP, WebAuthn)
- Token blacklisting
- Secrets manager integration
- SIEM integration for audit logs
