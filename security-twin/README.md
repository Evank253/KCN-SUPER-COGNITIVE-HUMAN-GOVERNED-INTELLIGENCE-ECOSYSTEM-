# KCN Security Twin v0.2

**DISPOSABLE · ISOLATED · AUTHORIZED TESTING ONLY**

Hardened twin of the KCN security surface for controlled external testing.

## Controls (v0.2)

| Control | Behavior |
|--------|----------|
| **Login rate limit / lockout** | 5 failures in 120s → 60s lockout (per username+client). Returns **429** + `Retry-After`. |
| **Token blacklist** | Logout revokes access (and optional refresh) by `jti`. Reuse → **401**. Refresh rotates and revokes old refresh. |
| **Strict JWT** | Requires `exp`, `iat`, `sub`, `iss=kcn-security-twin`, `type`, `twin=true`, valid signature. Altered tokens fail. |
| **Request size limits** | Body > 64 KiB → **413**. Memory content max 4096 chars, max 20 tags. |
| **Audit log** | Every event marked `TWIN TEST LOG — NOT PRODUCTION`. Export via admin. |

## Quick start

```bash
cd security-twin
docker compose up --build
```

- Twin: http://localhost:8100
- Docs: http://localhost:8100/docs

### Stub credentials

| Username     | Password              |
|--------------|-----------------------|
| `twin-admin` | `twin-pass-change-me` |
| `twin-user`  | `twin-user-pass`      |

## Logout with blacklist

Send the access token as Bearer. Optionally include refresh in JSON body to revoke both:

```bash
curl -X POST http://localhost:8100/api/v1/auth/logout \
  -H "Authorization: Bearer $ACCESS" \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"$REFRESH"}'
```

After logout, the same access token must return **401** on protected routes.

## Audit export

```bash
# login as twin-admin, then:
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8100/api/v1/audit/summary

curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8100/api/v1/audit/export?format=jsonl" \
  -o kcn-twin-audit.jsonl
```

## What these logs prove

Activity against **this disposable twin only**. Not production. Not a claim that KCN is the strongest system ever built.

When finished: `docker compose down -v`
